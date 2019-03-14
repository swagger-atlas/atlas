from collections import defaultdict
from copy import deepcopy
import json
import re

from atlas.conf import settings
from atlas.modules import constants, exceptions, mixins
from atlas.modules.transformer import profile_constants
from atlas.modules.transformer.base import models
from atlas.modules.transformer.artillery import templates


class Task(models.Task):
    """
    Input:
        A single Swagger Operation

    Output:
        Requisite load test functions and configuration required for that task.
        For Artillery:
            1. YAML configuration describing the URL, Method and processor function
            2. Create a processor function which needs to be executed before hitting the request.
                This is responsible for generating data for request body, parsing URL, and generating headers
                Also start the timing for influxDB
                All pre-request hooks for this OP are evaluated here
            3. Create a processor function which needs to be executed after getting the response
                This checks whether the response was valid
                Responsible for emitting correct error messages if invalid response
                For correct responses, parse the response, and capture the data for next APIs
                Write the Statistics in influxDB
            4. Create a processor function which checks whether this request needs to be hit
                Used when we want to restrict the APIs due to same user settings
                Eg: Profile Tags
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.before_func_name = f"{self.func_name}PreReq"
        self.after_func_name = f"{self.func_name}PostRes"
        self.if_true_func_name = f"{self.func_name}Condition"

        self.yaml_task = {}

    @property
    def tag_check(self) -> bool:
        """
        Check whether user has enabled TAGS, and this API has defined Tags
        :return: boolean
        """
        return self.open_api_op.tags and settings.ONLY_TAG_API

    def error_template_list(self, try_statements: list) -> list:
        """
        A wrapper function for Provider Check

        It takes in list of JS statements which needs to evaluate Provider
        It wraps them in try-except block, and raise the error as necessary
        And returns that list of JS statements

        :param try_statements: All the try statements in an array

        Sample Usage:
        Input:
            [ "provider.dummy()"]
        Output:
            [
                "try {",
                "   provider.dummy()",
                "} catch (ex) {,
                " ... " // Error statements here
                "}"
            ]
        """
        statements = [
            "try {",
        ]
        statements.extend(["{}{}".format(" "*4, try_statement) for try_statement in try_statements])
        statements.append("} catch (ex) {")
        catch_statements = [
            f"""console.error(ex.message + ' failed for "{self.open_api_op.op_id}"');""",
            "ee.emit('error', 'Provider Check Failed');",
            "return next();"
        ]
        statements.extend(["{}{}".format(" " * 4, statement) for statement in catch_statements])
        statements.append("}")
        return statements

    def normalize_function_name(self) -> str:
        """
        Returns camelCase format for func_names for Open API Operation
        """
        snake_case = re.sub("-", "_", self.open_api_op.func_name)
        return "".join([x.title() if idx > 0 else x for idx, x in enumerate(snake_case.split("_"))])

    @staticmethod
    def get_format_url_params() -> str:
        return ", ".join(['url', 'queryConfig', 'pathConfig', 'provider'])

    def if_true_function(self) -> str:
        """
        IF True function is used to determine whether this OPEN API should be hit as part of current workflow
        """
        return templates.IF_TRUE_FUNCTION.format(
            if_true_name=self.if_true_func_name,
            tags=", ".join([f"'{tag}'" for tag in self.open_api_op.tags])
        )

    def add_url_config_to_body(self, body: list) -> list:
        """
        Evaluates URL Parameters (Query and path parameters) and then add them to BEFORE_REQUEST function as needed
        """

        query_str, path_str = self.parse_url_params_for_body()

        # If there is no Query or Path params, we do not need to add them
        if query_str != "{}" or path_str != "{}":
            body.append("let urlConfig = [];")

            # If one if present, we need to append both
            body.append(f"const queryConfig = {query_str};")
            body.append(f"const pathConfig = {path_str};")

            # Also get Path Parameters
            body.extend(self.error_template_list(
                [
                    f"urlConfig = formatURL({self.get_format_url_params()});",
                    "url = urlConfig[0];",
                ]
            ))
        return body

    def body_definition(self) -> list:
        """
        This is where majority of work in constructing JS statements is done
        This is responsible for creating BEFORE_REQUEST function

        Major data structures:
            body: Body consists of list of JS statements for BEFORE_REQUEST statement
        """

        body = ["const provider = context.vars['provider'];"]

        if self.data_body:
            body.append(f"const bodyConfig = {json.dumps(self.data_body)};")

        body.append(f"let url = '{self.open_api_op.url}';")
        body.append(f"context.vars._rawURL = url;")

        if self.open_api_op.dependent_resources:
            body.append(f"provider.getRelatedResources({list(self.open_api_op.dependent_resources)});")

        body = self.add_url_config_to_body(body)

        body.append("let headers = _.cloneDeep(defaultHeaders);")
        if self.headers:
            body.append(f"let header_config = {{{', '.join(self.headers)}}};")
            body.extend(self.error_template_list(["_.merge(headers, provider.resolveObject(header_config));"]))

        request_params = {
            "headers": "headers"
        }
        request_param_str = ""
        for key, value in request_params.items():
            request_param_str += f"'{key}': {value}"
        body.append("let reqParams = {{{}}};".format(request_param_str))

        # Param Array is legacy data structure from prev. load test renditions (K6) which required an array in this form
        # In a refactoring, it could be split off in individual components for body, url and params
        # If we do that however, we would need to update HOOKS also
        param_array = ["url"]
        if self.open_api_op.method != constants.GET:
            body.append("let body = {};")       # We need body to be part of Function scope, and not try/catch scope
            if self.data_body:
                body.extend(self.error_template_list(["body = provider.resolveObject(bodyConfig);"]))
            param_array.append("body")
        param_array.append("reqParams")

        # before request Hooks ideally return what was passed to them. So reqArgs structure is same as param_array
        body.append("let reqArgs = hook.call('{op_id}', ...{args});".format(
            op_id=self.open_api_op.op_id, args="[{}]".format(", ".join(param_array))
        ))

        if "body" in param_array:
            body = self.handle_mime(body)

        body.append("requestParams.url = reqArgs[0];")
        body.append(f"requestParams.headers = reqArgs[{len(param_array) - 1}].headers;")

        # We need to store the resource we deleted in Context
        # This is needed if DELETE API fails, we need to restore the value to resource in our Shadow/Cache DB
        if self.delete_url_resource:
            _resource = getattr(self.delete_url_resource, constants.RESOURCE)
            _field = self.delete_url_resource.field
            body.append(f"context.vars._delete_resource = {{ resource: '{_resource}', value: urlConfig[1].{_field} }};")

        # Start the clock for Influx DB timing operations
        body.append(f"context.vars._startTime = Date.now();")

        return self.cache_operation_tasks(body)

    def handle_mime(self, body: list) -> list:
        """
        This is responsible for correctly identifying Consume resource for Operation
        Based on consume resource,
            - it adds correct headers
            - it sends body in correct format (json/formData etc)
        """
        mime = self.open_api_op.mime

        # Check if this request has any files associated.
        # If there are files, we automatically assume formData as response, and 'multipart/formData' as accept header
        if self.has_files():
            # Form Data has requirement that it only takes String or Buffer as its value
            # So we explicitly converts everything in string, except for Streams (which are our files)
            body.extend([
                "let formData = {};",
                "_.forEach(reqArgs[1], (val, key) => {",
                "    val instanceof stream.Readable ? formData[key] = val : formData[key] = _.toString(val); ",
                "});",
                "requestParams.formData = formData;"
            ])
        else:
            request_map = {
                constants.JSON_CONSUMES: "json",
                constants.FORM_CONSUMES: "form",
                constants.MULTIPART_CONSUMES: "formData"
            }

            body.append(f"reqArgs[2].headers['Content-Type'] = '{mime}';")
            body.append(f"requestParams.{request_map[mime]} = reqArgs[1];")

        return body

    def cache_operation_tasks(self, body: list) -> list:
        """
        Define the definition for tasks which are responsible for updating the cached data
        (i.e. resource DB we maintain)
        """

        response = self.parse_responses(self.open_api_op.responses)
        if response:
            self.post_check_tasks.append(
                f"context.vars['respDataParser'].resolve("
                f"{json.dumps(response)}, extractBody(response, requestParams, context), provider.configResourceMap);"
            )

        return body

    def set_yaml_definition(self) -> None:
        """
        Define config for task in Artillery YAML File
        """
        self.yaml_task = {
            self.open_api_op.method: {
                "url": self.open_api_op.url,
                "beforeRequest": self.before_func_name,
                "afterResponse": self.after_func_name
            }
        }

        if self.tag_check:
            self.yaml_task[self.open_api_op.method]["ifTrue"] = self.if_true_func_name

    def pre_request_function(self, width: int) -> str:
        """
        Wrapper for BEFORE REQUEST function
        """
        statements = [
            f"function {self.before_func_name}(requestParams, context, ee, next) {{",
            "{w}{body}".format(w=' ' * width * 4, body="\n{w}".format(w=' ' * width * 4).join(self.body_definition())),
            "{w}return next();".format(w=' ' * width * 4),
            "}"
        ]
        return "\n".join(statements)

    def post_response_function(self, width: int) -> str:
        """
        AFTER_RESPONSE function definition
        """

        else_body = "\n".join([
            "",
            "{w}}} else {{".format(w=' ' * width * 4),
            "{w}{body}".format(
                w=' ' * (width + 1) * 4, body="\n{w}".format(w=' ' * (width + 1) * 4).join(self.post_check_tasks)
            )
        ]) if self.post_check_tasks else ""

        return templates.API_AFTER_RESPONSE_FUNCTION.format(
            after_func_name=self.after_func_name,
            else_body=else_body
        )

    def convert(self, width: int) -> list:
        """
        Entry Point for the class.

        Calls all the respective functions and compile them

        :param
            :width: Indentation tabs to be used
        """

        self.set_yaml_definition()
        statements = [self.pre_request_function(width), self.post_response_function(width)]

        if self.tag_check:
            statements.append(self.if_true_function())

        return statements


class TaskSet(models.TaskSet):
    """
    Responsible for collating all Tasks (as defined by Task Model) and scenarios

    INPUT:
        List of Task objects. (Artillery Task class is defined in artillery/models.py)
        Scenarios: As defined in settings. If scenarios are not passed, we construct our own scenario.

    Output:
        Artillery YAML:
            Construct multiple scenarios as needed, and create different flows in artillery YAML.
        Processor JS:
            Collects all Task Processor functions, and add them in a cohesive manner
            Add the common functions which are required by individual tasks
            Add export statements for requisite functions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.yaml_flow = []

        # Map of Task OP ID to its YAML configuration
        self.task_map = {}

        self.scenario_profile_map = defaultdict(list)

    def construct_profile_scenario_map(self) -> None:
        """
        User defines scenarios for each profile.

        However, we need a reverse mapping, that given a scenario, give all profiles which could be used to execute it.
        So, this function constructs that map.

        It also validates that for each scenario, there is at least one profile which could be used
        """
        yaml_reader = mixins.YAMLReadWriteMixin()
        profiles = yaml_reader.read_file_from_input(settings.PROFILES_FILE, {})

        for name, config in profiles.items():
            scenario_list = config.get(profile_constants.SCENARIOS, [profile_constants.DEFAULT_SCENARIO])

            for scenario_name in scenario_list:
                self.scenario_profile_map[scenario_name].append(name)

        # Validate that All scenarios have at least one profile associated.
        # If not, throw a warning and remove that scenario
        unlinked_scenarios = set(self.scenarios.keys()) - set(self.scenario_profile_map.keys())
        for scenario_name in unlinked_scenarios:
            print(f"WARNING: {scenario_name} scenario is not linked to any profile. Will not be part of Artillery\n")
            self.scenarios.pop(scenario_name)

    def construct_task_map(self) -> None:
        self.task_map = {_task.open_api_op.op_id: _task.yaml_task for _task in self.tasks}

    def make_yaml_scenario(self, name: str, flow_tasks: list) -> dict:
        """
        For Artillery YAML, define configuration for any single scenario

        :param name: Name of scenario
        :param flow_tasks: List of tasks in the scenario

        :return: Python dict representing YAML for config
        """

        flow_definition = [{"function": f"{name}SetProfiles"}, {"function": "setUp"}]

        try:
            # Nested Shallow copy leads to explicit referencing in YAML which is not clear
            flow_definition.extend([deepcopy(self.task_map[task_key.strip()]) for task_key in flow_tasks])
        except KeyError as exc:
            raise exceptions.InvalidSettingsException(f"Invalid Key in Scenario {name}: {exc}")
        flow_definition.append({"function": "endResponse"})
        return {
            "flow": flow_definition,
            "name": name
        }

    def set_yaml_flow(self) -> None:
        """
        Define Artillery YAML for all scenarios
        """

        self.construct_task_map()
        for name, scenario in self.scenarios.items():
            self.yaml_flow.append(self.make_yaml_scenario(name, scenario))

    def scenario_profile_setup(self, name: str) -> str:
        """
        Construct and return Javascript function which selects profile given a scenario
        """
        return templates.SCENARIO_PROFILE_FUNCTION.format(
            name=name,
            profiles=", ".join([f"'{profile}'" for profile in self.scenario_profile_map.get(name, [])])
        )

    def task_definitions(self, width: int) -> str:
        """
        Construct JS Program Snippet containing all processor functions as defined by task
        """

        join_string = "\n\n".format(w=' ' * width * 4)
        tasks = [self.scenario_profile_setup(scenario) for scenario in self.scenarios]
        for _task in self.tasks:
            tasks.extend(_task.convert(width))
        return join_string.join(tasks)

    @staticmethod
    def task_func_declarations(task: Task, width: int) -> str:
        """
        Construct the function declarations for Task processor functions
        """

        statements = [
            "{w}{func}: {func},".format(w=' '*width*4, func=task.before_func_name),
            "{w}{func}: {func},".format(w=' '*width*4, func=task.after_func_name)
        ]

        if task.tag_check:
            statements.append("{w}{func}: {func},".format(w=' '*width*4, func=task.if_true_func_name))

        return "\n".join(statements)

    def processor_export_statements(self, width: int) -> str:
        """
        Construct and return JS Program Snippet which exports required functions.
        These functions need to be exported so that Artillery could use them
        """

        indent = ' '*width*4
        return "\n".join([
            "module.exports = {",
            f"{indent}setUp: setUp,",
            "\n".join([f"{indent}{name}SetProfiles: {name}SetProfiles," for name in self.scenarios]),
            "\n".join([self.task_func_declarations(_task, width) for _task in self.tasks]),
            f"{indent}endResponse: statsEndResponse",
            "};"
        ])

    def convert(self, width: int) -> str:
        """
        Entry point for this method.

        It is responsible for constructing both YAML and JS Snippets for Artillery

        YAML construction is saved in self.yaml_task, and JS Code snippet is returned from this function
        """

        self.construct_profile_scenario_map()

        statements = [
            self.processor_export_statements(width),
            templates.SELECT_PROFILE_FUNCTION,
            templates.REGISTER_HOOKS_FUNCTION,
            templates.SETUP_FUNCTION,
            templates.DYNAMIC_TEMPLATE_FUNCTION,
            templates.FORMAT_URL_FUNCTION,
            templates.EXTRACT_BODY_FUNCTION,
            templates.STATS_WRITER,
            templates.FINAL_FLOW_FUNCTION,
            "\n",
            self.task_definitions(width)
        ]

        # Make sure that YAML is constructed after all task definitions have been constructed
        self.set_yaml_flow()

        return "\n".join(statements)
