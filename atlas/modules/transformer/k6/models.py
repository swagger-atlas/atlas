import json
import re

from atlas.modules import constants, utils
from atlas.modules.transformer.base import models
from atlas.conf import settings


class Task(models.Task):
    """
    Define a function which is responsible for hitting single URL with single method
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.before_func_name = f"{self.func_name}PreReq"
        self.after_func_name = f"{self.func_name}PostRes"

        self.yaml_task = {}

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
            "check(ex, {'providerCheck': () => false});",
            "return;"
        ]
        statements.extend(["{}{}".format(" " * 4, statement) for statement in catch_statements])
        statements.append("}")
        return statements

    def normalize_function_name(self):
        snake_case = re.sub("-", "_", self.open_api_op.func_name)
        return "".join([x.title() if idx > 0 else x for idx, x in enumerate(snake_case.split("_"))])

    def get_format_url_params(self):
        params = ['url', 'queryConfig', 'pathConfig']
        if self.open_api_op.method == constants.DELETE:
            params.append("{'delete': true}")
        return ", ".join(params)

    def body_definition(self):
        body = list()

        if self.data_body:
            body.append("const bodyConfig = {config};".format(config=json.dumps(self.data_body)))

        if self.open_api_op.tags and settings.ONLY_TAG_API:
            body.append("const tags = [{}];".format(", ".join(["'{}'".format(tag) for tag in self.open_api_op.tags])))
            body.append("if (_.isEmpty(_.intersection(tags, profile.profile.tags || []))){")
            body.append("{}return;".format(" "*4))
            body.append("}")

        query_str, path_str = self.parse_url_params_for_body()

        body.append(f"let url = '{self.open_api_op.url}';")

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

        # We can pick this up from Swagger Also
        mime = "json"
        if mime == "json" and "body" in param_array:
            body.append("requestParams.json = reqArgs[1];")
            body.append("reqArgs[2].headers['Content-Type'] = 'application/json';")

        if self.open_api_op.method == constants.POST:
            # This is incorrect, but would work for Simple strings as long as char length is equal to byte length
            # Since most of the data is generated by us, it should be fine
            body.append("reqArgs[2].headers['Content-Length'] = reqArgs[1].length;")

        body.append("requestParams.url = reqArgs[0];")
        body.append(f"requestParams.headers = reqArgs[{len(param_array) - 1}];")

        return self.cache_operation_tasks(body)

    def cache_operation_tasks(self, body):
        """
        Define the definition for tasks which are responsible for updating the cached data
        """

        response = self.parse_responses(self.open_api_op.responses)
        if response:
            self.post_check_tasks.append(f"respDataParser.parser({response}, response);")

        return body

    def set_yaml_definition(self):
        self.yaml_task = {
            self.open_api_op.method: {
                "url": self.open_api_op.url,
                "beforeRequest": self.before_func_name,
                "afterResponse": self.after_func_name
            }
        }

    def pre_request_function(self, width):
        statements = [
            f"function {self.before_func_name}(requestParams, context, ee, next) {{",
            "{w}{body}".format(w=' ' * width * 4, body="\n{w}".format(w=' ' * width * 4).join(self.body_definition())),
            "{w}return next();".format(w=' ' * width * 4),
            "}"
        ]
        return "\n".join(statements)

    def post_response_function(self, width):
        statements = [
            f"function {self.after_func_name}(requestParams, response, context, ee, next) {{",
            "{w}{body}".format(w=' ' * width * 4, body="\n{w}".format(w=' ' * width * 4).join(self.post_check_tasks)),
            "{w}return next();".format(w=' ' * width * 4),
            "}"
        ]
        return "\n".join(statements)

    def convert(self, width):

        self.set_yaml_definition()
        return [self.pre_request_function(width), self.post_response_function(width)]


class TaskSet(models.TaskSet):
    """
    Function containing collection of tasks
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.yaml_flow = {}

    def set_yaml_flow(self):
        self.yaml_flow = {
            "flow": [_task.yaml_task for _task in self.tasks]
        }

    def task_definitions(self, width):
        join_string = "\n\n".format(w=' ' * width * 4)
        tasks = []
        for _task in self.tasks:
            tasks.extend(_task.convert(width))
        return join_string.join(tasks)

    @staticmethod
    def func_exports(task, width):
        return "\n".join([
            "{w}{func}: {func},".format(w=' '*width*4, func=task.before_func_name),
            "{w}{func}: {func},".format(w=' '*width*4, func=task.after_func_name)
        ])

    @staticmethod
    def format_url(width):
        statements = [
            "function formatURL(url, queryConfig, pathConfig, options) {",
            "const pathParams = provider.resolveObject(pathConfig, options);",
            "url = dynamicTemplate(url, pathParams);",
            "const queryParams = provider.resolveObject(queryConfig);",
            "const queryString = Object.keys(queryParams).map(key => key + '=' + queryParams[key]).join('&');",
            "url = queryString? url + '?' + queryString : url;",
            "return [url, _.assign(pathParams, queryParams)];"
        ]
        join_string = "\n{w}".format(w=' ' * width * 4)
        return join_string.join(statements) + "\n}"

    @staticmethod
    def dynamic_template(width):
        statements = [
            "function dynamicTemplate(string, vars) {",
            "_.forIn(vars, function (value, key) {",
            "{w}string = string.replace(new RegExp('({{' + key + '}})', 'gi'), value);".format(w=' ' * width * 4),
            "});",
            "return string;"
        ]
        join_string = "\n{w}".format(w=' ' * width * 4)
        return join_string.join(statements) + "\n}"

    def task_calls(self, width):
        return "\n".join([
            "module.exports = {",
            "\n".join([self.func_exports(_task, width) for _task in self.tasks]),
            "};"
        ])

    def convert(self, width):
        statements = [
            "provider = new Provider(profile.profileName);",
            "respDataParser = new ResponseDataParser(profile.profileName);",
            f"\n{self.task_calls(width)}",
            "\n",
            self.dynamic_template(width),
            "\n",
            self.format_url(width),
            "\n",
            self.task_definitions(width)
        ]

        self.set_yaml_flow()
        return "\n".join(statements)
