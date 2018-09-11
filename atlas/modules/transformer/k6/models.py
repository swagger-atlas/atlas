import re

from atlas.modules import constants, utils
from atlas.modules.transformer.base import models
from atlas.modules.transformer.k6 import constants as k6_constants
from atlas.conf import settings

PYTHON_TEMPLATE_PATTERN = re.compile(r"{(.*?)}")
JS_TEMPLATE_PATTERN = "${\\1}"


class Task(models.Task):
    """
    Define a function which is responsible for hitting single URL with single method
    """

    @staticmethod
    def error_template_list(try_statements: list) -> list:
        """
        :param try_statements: All the try statements in an array
        """
        statements = [
            "try {",
        ]
        statements.extend(["{}{}".format(" "*4, try_statement) for try_statement in try_statements])
        statements.append("} catch (ex) {")
        catch_statements = [
            "console.error(ex.message);",
            "check(ex, {'providerCheck': () => false});",
            "return;"
        ]
        statements.extend(["{}{}".format(" " * 4, statement) for statement in catch_statements])
        statements.append("}")
        return statements

    def normalize_function_name(self):
        snake_case = re.sub("-", "_", self.open_api_op.func_name)
        return "".join([x.title() if idx > 0 else x for idx, x in enumerate(snake_case.split("_"))])

    def body_definition(self):
        body = list()

        if self.data_body:
            body.append("const bodyConfig = {config};".format(config=self.data_body))

        if self.open_api_op.tags and settings.ONLY_TAG_API:
            body.append("const tags = [{}];".format(", ".join(["'{}'".format(tag) for tag in self.open_api_op.tags])))
            body.append("if (_.isEmpty(_.intersection(tags, hook.tags))){")
            body.append("{}return;".format(" "*4))
            body.append("}")

        query_str, path_str = self.parse_url_params_for_body()

        js_url = re.sub(PYTHON_TEMPLATE_PATTERN, JS_TEMPLATE_PATTERN, self.open_api_op.url)
        url_str = "let url = baseURL + '{}';".format(js_url)

        body.append(url_str)

        if query_str != "{}" or path_str != "{}":
            # If one if present, we need to append both
            body.append("const queryConfig = {q};".format_map(utils.StringDict(q=query_str)))
            body.append("const pathConfig = {p};".format_map(utils.StringDict(p=path_str)))

            # Also get Path Parameters
            body.extend(self.error_template_list(
                ["url = formatURL(url, queryConfig, pathConfig);"]
            ))

        body.append("let headers = _.cloneDeep(defaultHeaders);")
        if self.headers:
            body.extend(self.error_template_list(["_.merge(headers, provider.generateData(header_config));"]))

        request_params = {
            "headers": "headers"
        }
        request_param_str = ""
        for key, value in request_params.items():
            request_param_str += "'{name}': {config}".format(name=key, config=value)
        body.append("let requestParams = {{{}}};".format(request_param_str))

        param_array = ["url"]
        if self.open_api_op.method != constants.GET:
            body.append("let body = {};")       # We need body to be part of Function scope, and not try/catch scope
            if self.data_body:
                body.extend(self.error_template_list(["body = provider.generateData(bodyConfig);"]))
            param_array.append("body")
        param_array.append("requestParams")

        body.append("let reqArgs = hook.call('{op_id}', ...{args});".format(
            op_id=self.open_api_op.func_name, args="[{}]".format(", ".join(param_array))
        ))

        return body

    def get_function_definition(self, width):

        body = self.body_definition()

        body.append("let res = http.{method}(...reqArgs);".format(
            method=k6_constants.K6_MAP.get(self.open_api_op.method, self.open_api_op.method)
        ))

        check_statement = "check(res, {'resp is 2xx': (r) => (r.status >= 200 && r.status < 300) });"

        body.append(check_statement)
        return "\n{w}".format(w=' ' * width * 4).join(body)

    def convert(self, width):
        statements = [
            "function {func_name}() {{".format(func_name=self.func_name),
            "{w}{body}".format(w=' ' * width * 4, body=self.get_function_definition(width)),
            "}"
        ]
        return "\n".join(statements)


class TaskSet(models.TaskSet):
    """
    Function containing collection of tasks
    """

    def task_definitions(self, width):
        join_string = "\n\n".format(w=' ' * width * 4)
        return join_string.join([_task.convert(width) for _task in self.tasks])

    @staticmethod
    def group_statement(task):
        return "group('{func_name}', {func_name});".format(func_name=task.func_name)

    @staticmethod
    def format_url(width):
        statements = [
            "function formatURL(url, queryConfig, pathConfig) {",
            "const pathParams = provider.generateData(pathConfig);",
            "url = dynamicTemplate(url, pathParams);",
            "const queryParams = provider.generateData(queryConfig);",
            "const queryString = Object.keys(queryParams).map(key => key + '=' + params[key]).join('&');",
            "url = queryString? url + '?' + queryString : url;",
            "return url;"
        ]
        join_string = "\n{w}".format(w=' ' * width * 4)
        return join_string.join(statements) + "\n}"

    @staticmethod
    def dynamic_template(width):
        statements = [
            "function dynamicTemplate(string, vars) {",
            "const keys = Object.keys(vars);",
            "const values = Object.values(vars);",
            r"let func = new Function(...keys, `return \`${string}\`;`);",
            "return func(...values);"
        ]
        join_string = "\n{w}".format(w=' ' * width * 4)
        return join_string.join(statements) + "\n}"

    def task_calls(self, width):
        join_string = "\n{w}".format(w=' ' * width * 4)
        return join_string.join([self.group_statement(_task) for _task in self.tasks])

    def convert(self, width):
        statements = [
            "export default function() {",
            "{w}{task_calls}".format(task_calls=self.task_calls(width), w=' ' * width * 4),
            "}",
            "\n",
            self.dynamic_template(width),
            "\n",
            self.format_url(width),
            "\n",
            self.task_definitions(width)
        ]

        return "\n".join(statements)
