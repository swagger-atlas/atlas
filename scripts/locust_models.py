import logging
import random
import string

from scripts import (
    utils
)

logger = logging.getLogger(__name__)


class Task:
    """
    Define a single Task of Locust File
    """

    def __init__(self, func_name, method, url, parameters=None):

        self.func_name = func_name
        self.method = method
        self.url = url
        self.parameters = parameters or {}

        self.decorators = ["@task(1)"]

    @staticmethod
    def get_function_parameters():
        parameter_list = ["self", "format_url", "**kwargs"]
        return ", ".join(parameter_list)

    def get_function_declaration(self, width):
        return "{decorators}\n{w}def {name}({parameters}):".format(**utils.StringDict(
            decorators=self.get_decorators(width), name=self.func_name, parameters=self.get_function_parameters(),
            w='\t' * width)
                                                                   )

    @staticmethod
    def get_client_parameters():
        parameter_list = ["format_url"]
        return ", ".join(parameter_list)

    def get_function_definition(self, width):
        return "self.client.{method}({params})".format(**utils.StringDict(
            method=self.method, params=self.get_client_parameters()
        ))

    def get_decorators(self, width):
        return "\n{w}".join(self.decorators).format_map(utils.StringDict(w='\t' * width))

    def convert(self, width):
        """
        Convert the task to function
        """

        components = ["{declaration}", "{definition}"]
        return "\n{w}".join(components).format(**utils.StringDict(
            declaration=self.get_function_declaration(width - 1), definition=self.get_function_definition(width),
            w='\t' * width
        ))


class TaskSet:

    def __init__(self, tasks, tag=None):
        self.tag = tag or ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.tasks = tasks

    def generate_tasks(self, width):
        return "\n\n{w}".join([_task.convert(width) for _task in self.tasks]).format_map(
            utils.StringDict(w='\t' * width))

    @staticmethod
    def generate_on_start():
        return ""

    @property
    def task_set_name(self):
        return self.tag + "Behaviour"

    def get_behaviour(self, width):
        return "class {klass}(TaskSet):\n\t{on_start}\n\t{tasks}".format(**utils.StringDict(
            klass=self.task_set_name,
            on_start=self.generate_on_start(),
            tasks=self.generate_tasks(width + 1)
        ))

    def locust_properties(self, width):
        properties = {
            "task_set": self.task_set_name,
            "min_wait": 5000,
            "max_wait": 9000
        }
        return "\n{w}".join(
            ["{key} = {value}".format(key=key, value=value) for key, value in properties.items()]
        ).format(**utils.StringDict(w='\t' * width))

    def get_locust(self, width):
        return "class {klass}(HttpLocust):\n\t{properties}".format(**utils.StringDict(
            klass=self.tag + "Locust",
            properties=self.locust_properties(width)
        ))

    def convert(self, width):
        return "{task_set}\n\n{locust}".format(**utils.StringDict(
            task_set=self.get_behaviour(width),
            locust=self.get_locust(width)
        ))
