import re

from modules import constants, utils
from modules.transformer.base import models
from modules.transformer.k6 import constants as k6_constants

PYTHON_TEMPLATE_PATTERN = re.compile(r"{(.*?)}")
JS_TEMPLATE_PATTERN = "${\\1}"


class Task(models.Task):
    """
    Define a function which is responsible for hitting single URL with single method
    """

    @staticmethod
    def normalize_function_name(func_name):
        snake_case = re.sub("-", "_", func_name)
        return "".join([x.title() if idx > 0 else x for idx, x in enumerate(snake_case.split("_"))])

    def body_definition(self):
        body = list()

        if self.data_body:
            body.append("const body_config = {config};".format(config=self.data_body))

        query_params = []
        path_params = []

        param_map = {
            "query": query_params,
            "path": path_params
        }
        for key, value in self.url_params.items():
            param_str = "'{name}': {config}".format(name=key, config=value[1])
            param_map[value[0]].append(param_str)

        query_str = "{}"
        path_str = "{}"
        js_url = re.sub(PYTHON_TEMPLATE_PATTERN, JS_TEMPLATE_PATTERN, self.url)
        url_str = "let url = '{}';".format(js_url)

        body.append(url_str)

        if query_params:
            query_str = "{" + ", ".join(query_params) + "}"

        if path_params:
            path_str = "{" + ", ".join(path_params) + "}"

        if query_str != "{}" or path_str != "{}":
            # If one if present, we need to append both
            body.append("const queryConfig = {q};".format_map(utils.StringDict(q=query_str)))
            body.append("const pathConfig = {p};".format_map(utils.StringDict(p=path_str)))

            # Also get Path Parameters
            body.append(
                "url = formatURL(url, queryConfig, pathConfig);"
            )

        if self.headers:
            body.append("let headers = defaultHeaders;")
            body.append("_.merge(headers, provider.generateData(header_config))")

        return body

    def get_http_method_parameters(self):

        parameters = [
            "baseURL + url"
        ]

        if self.method != constants.GET:
            parameters.append("provider.generateData(body_config)" if self.data_body else "{}")

        request_params = {
            "headers": "headers" if self.headers else "defaultHeaders"
        }
        request_param_str = ""
        for key, value in request_params.items():
            request_param_str += "'{name}': {config}".format(name=key, config=value)
        parameters.append("{" + request_param_str + "}")

        return ", ".join(parameters)

    def get_function_definition(self, width):

        body = self.body_definition()

        body.append("let res = http.{method}({parameters});".format(
            parameters=self.get_http_method_parameters(), method=k6_constants.K6_MAP.get(self.method, self.method)
        ))

        check_statement = "check(res, {'success_resp': (r) => (r.status >= 200 && r.status < 300) });"

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
            "let func = new Function(...keys, `return \`${string}\`;`);",
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
