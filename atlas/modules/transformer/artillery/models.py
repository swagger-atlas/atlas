import json
import re

from atlas.modules import constants, utils
from atlas.modules.transformer.base import models
from atlas.conf import settings
from atlas.modules.transformer.artillery import templates


class Task(models.Task):
    """
    Define a function which is responsible for hitting single URL with single method
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.before_func_name = f"{self.func_name}PreReq"
        self.after_func_name = f"{self.func_name}PostRes"
        self.if_true_func_name = f"{self.func_name}Condition"

        self.yaml_task = {}

    @property
    def tag_check(self):
        return self.open_api_op.tags and settings.ONLY_TAG_API

    def error_template_list(self, try_statements: list) -> list:
        """
        :param try_statements: All the try statements in an array
        """
        statements = [
            "try {",
        ]
        statements.extend(["{}{}".format(" "*4, try_statement) for try_statement in try_statements])
        statements.append("} catch (ex) {")
        catch_statements = [
            "console.error(ex.message + ' failed for ' + '{}');".format(self.func_name),
            "ee.emit('error', 'Provider Check Failed');",
            "return next();"
        ]
        statements.extend(["{}{}".format(" " * 4, statement) for statement in catch_statements])
        statements.append("}")
        return statements

    def normalize_function_name(self):
        snake_case = re.sub("-", "_", self.open_api_op.func_name)
        return "".join([x.title() if idx > 0 else x for idx, x in enumerate(snake_case.split("_"))])

    @staticmethod
    def get_format_url_params():
        params = ['url', 'queryConfig', 'pathConfig', 'provider']
        return ", ".join(params)

    def validate_tags(self):
        body = []

        if self.tag_check:
            body.append("const tags = [{}];".format(", ".join(["'{}'".format(tag) for tag in self.open_api_op.tags])))
            body.append("return (!_.isEmpty(_.intersection(tags, contextVars['profile'].tags || [])));")

        return body

    def if_true_function(self, width):
        statements = [
            f"function {self.if_true_func_name}(contextVars) {{",
            "{w}{body}".format(w=' ' * width * 4, body="\n{w}".format(w=' ' * width * 4).join(self.validate_tags())),
            "}"
        ]
        return "\n".join(statements)

    def add_url_config_to_body(self, body):

        query_str, path_str = self.parse_url_params_for_body()
        if query_str != "{}" or path_str != "{}":
            body.append("let urlConfig = [];")

            # If one if present, we need to append both
            body.append("const queryConfig = {q};".format_map(utils.StringDict(q=query_str)))
            body.append("const pathConfig = {p};".format_map(utils.StringDict(p=path_str)))

            # Also get Path Parameters
            body.extend(self.error_template_list(
                [
                    f"urlConfig = formatURL({self.get_format_url_params()});",
                    "url = urlConfig[0];",
                ]
            ))
        return body

    def body_definition(self):
        body = ["const provider = context.vars['provider'];"]

        if self.data_body:
            body.append("const bodyConfig = {config};".format(config=json.dumps(self.data_body)))

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
            request_param_str += "'{name}': {config}".format(name=key, config=value)
        body.append("let reqParams = {{{}}};".format(request_param_str))

        param_array = ["url"]
        if self.open_api_op.method != constants.GET:
            body.append("let body = {};")       # We need body to be part of Function scope, and not try/catch scope
            if self.data_body:
                body.extend(self.error_template_list(["body = provider.resolveObject(bodyConfig);"]))
            param_array.append("body")
        param_array.append("reqParams")

        body.append("let reqArgs = hook.call('{op_id}', ...{args});".format(
            op_id=self.open_api_op.func_name, args="[{}]".format(", ".join(param_array))
        ))

        if "body" in param_array:
            body = self.handle_mime(body)

        if self.open_api_op.method == constants.POST:
            # This is incorrect, but would work for Simple strings as long as char length is equal to byte length
            # Since most of the data is generated by us, it should be fine
            body.append("reqArgs[2].headers['Content-Length'] = reqArgs[1].length;")

        body.append("requestParams.url = reqArgs[0];")
        body.append(f"requestParams.headers = reqArgs[{len(param_array) - 1}].headers;")

        body.append(f"context.vars._startTime = Date.now();")

        return self.cache_operation_tasks(body)

    def handle_mime(self, body):
        mime = self.open_api_op.mime

        request_map = {
            constants.JSON_CONSUMES: "json",
            constants.FORM_CONSUMES: "form",
            constants.MULTIPART_CONSUMES: "formData"
        }

        body.append(f"reqArgs[2].headers['Content-Type'] = '{mime}';")
        body.append(f"requestParams.{request_map[mime]} = reqArgs[1];")

        return body

    def cache_operation_tasks(self, body):
        """
        Define the definition for tasks which are responsible for updating the cached data
        """

        response = self.parse_responses(self.open_api_op.responses)
        if response:
            self.post_check_tasks.append(
                f"context.vars['respDataParser'].resolve("
                f"{json.dumps(response)}, extractBody(response, requestParams, context), provider.configResourceMap);"
            )

        return body

    def set_yaml_definition(self):
        self.yaml_task = {
            self.open_api_op.method: {
                "url": self.open_api_op.url,
                "beforeRequest": self.before_func_name,
                "afterResponse": self.after_func_name
            }
        }

        if self.tag_check:
            self.yaml_task[self.open_api_op.method]["ifTrue"] = self.if_true_func_name

    def pre_request_function(self, width):
        statements = [
            f"function {self.before_func_name}(requestParams, context, ee, next) {{",
            "{w}{body}".format(w=' ' * width * 4, body="\n{w}".format(w=' ' * width * 4).join(self.body_definition())),
            "{w}return next();".format(w=' ' * width * 4),
            "}"
        ]
        return "\n".join(statements)

    def post_response_function(self, width):

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

    def convert(self, width):

        self.set_yaml_definition()
        statements = [self.pre_request_function(width), self.post_response_function(width)]

        if self.tag_check:
            statements.append(self.if_true_function(width))

        return statements


class TaskSet(models.TaskSet):
    """
    Function containing collection of tasks
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.yaml_flow = {}

    def set_yaml_flow(self):
        flow_definition = [{"function": "setUp"}]
        flow_definition.extend([_task.yaml_task for _task in self.tasks])
        flow_definition.append({"function": "endResponse"})
        self.yaml_flow = {
            "flow": flow_definition
        }

    def task_definitions(self, width):
        join_string = "\n\n".format(w=' ' * width * 4)
        tasks = []
        for _task in self.tasks:
            tasks.extend(_task.convert(width))
        return join_string.join(tasks)

    @staticmethod
    def func_exports(task, width):

        statements = [
            "{w}{func}: {func},".format(w=' '*width*4, func=task.before_func_name),
            "{w}{func}: {func},".format(w=' '*width*4, func=task.after_func_name)
        ]

        if task.tag_check:
            statements.append("{w}{func}: {func},".format(w=' '*width*4, func=task.if_true_func_name))

        return "\n".join(statements)

    def task_calls(self, width):
        return "\n".join([
            "module.exports = {",
            "{w}setUp: setUp,".format(w=' '*width*4),
            "\n".join([self.func_exports(_task, width) for _task in self.tasks]),
            "{w}endResponse: statsEndResponse".format(w=' '*width*4),
            "};"
        ])

    def convert(self, width):
        statements = [
            self.task_calls(width),
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

        self.set_yaml_flow()
        return "\n".join(statements)
