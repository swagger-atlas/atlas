import re

from modules.transformer.base import models


class Task(models.Task):
    """
    Define a function which is responsible for hitting single URL with single method
    """

    @staticmethod
    def normalize_function_name(func_name):
        return re.sub("-", "_", func_name)

    def parse_parameters(self):
        pass

    def convert(self, width):
        statements = [
            "function {func_name}() {{".format(func_name=self.func_name),
            "{w}http.{method}('{url}')".format(w=' ' * width * 4, url=self.url, method=self.method),
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

    def task_calls(self, width):
        join_string = "\n{w}".format(w=' ' * width * 4)
        return join_string.join(["{}();".format(_task.func_name) for _task in self.tasks])

    def convert(self, width):
        statements = [
            "export default function() {",
            "{w}{task_calls}".format(task_calls=self.task_calls(width), w=' ' * width * 4),
            "}",
            "\n",
            self.task_definitions(width)
        ]

        return "\n".join(statements)
