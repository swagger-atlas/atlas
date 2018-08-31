import re

from modules.transformer.base import models
from modules.transformer.k6 import constants as k6_constants


class Task(models.Task):
    """
    Define a function which is responsible for hitting single URL with single method
    """

    @staticmethod
    def normalize_function_name(func_name):
        snake_case = re.sub("-", "_", func_name)
        return "".join([x.title() if idx > 0 else x for idx, x in enumerate(snake_case.split("_"))])

    def parse_parameters(self):
        pass

    def get_url_string(self):
        return "baseURL + '{url}'".format(url=self.url)

    def get_function_definition(self, width):
        body = list()

        body.append("let res = http.{method}({url});".format(
            url=self.get_url_string(), method=k6_constants.K6_MAP.get(self.method, self.method)
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

    def task_calls(self, width):
        join_string = "\n{w}".format(w=' ' * width * 4)
        return join_string.join([self.group_statement(_task) for _task in self.tasks])

    def convert(self, width):
        statements = [
            "export default function() {",
            "{w}{task_calls}".format(task_calls=self.task_calls(width), w=' ' * width * 4),
            "}",
            "\n",
            self.task_definitions(width)
        ]

        return "\n".join(statements)
