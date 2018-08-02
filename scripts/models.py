import logging
import random
import string
from collections import OrderedDict

from scripts import (
    constants as swagger_constants,
    exceptions,
    utils
)

logger = logging.getLogger(__name__)

specs = {
    "paths": {
        "/api/user/{id}": {
            "parameters": [
                {
                    "in": "path",
                    "name": "id",
                    "type": "integer",
                    "required": True
                }
            ],
            "get": {
                "summary": "This is sample API Summary",
                "operationID": "retrieveUser",
                "responses": {
                    "200": {
                        "description": "User Object",
                        "schema": {
                            "$ref": "#/definitions/user"
                        }
                    }
                }
            }
        }
    },
    "definitions": {
        "user": {
            "type": "object",
            "properties": {
                "id": {},
                "name": {}
            }
        }
    }
}


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


class Operation:
    """
    Define an OpenAPI Specific Operation
    """

    def __init__(self, url, method, config, spec=None):

        self.url = url
        self.method = method
        self.config = config

        # Complete Swagger Spec Model
        self.spec = spec or {}

        self.parameters = OrderedDict()

    def validate_method(self):
        if self.method not in swagger_constants.VALID_METHODS:
            raise exceptions.ImproperSwaggerException("Invalid Method -%s for %s", self.method, self.url)

    def add_parameters(self, parameters):

        # ASSUMPTION: We will assume that our parameters are not defined by refs
        # This seems a valid assumption considering that none of Swagger Generators do that right now

        for parameter in parameters:
            name = parameter.pop(swagger_constants.PARAMETER_NAME, None)

            if not name:
                raise exceptions.ImproperSwaggerException("Parameter configuration does not have name - %s", parameter)

            self.parameters[name] = parameter

    def get_task(self):

        func_name = self.config.get(swagger_constants.OPERATION)
        self.add_parameters(self.config.get(swagger_constants.PARAMETERS, []))

        return Task(func_name=func_name, parameters=self.parameters, url=self.url, method=self.method)


class OpenAPISpec:

    def __init__(self, spec):
        self.spec = spec

        self.paths = OrderedDict()
        self.tasks = []

    def get_tasks(self):

        paths = self.spec.get(swagger_constants.PATHS, {})

        for path, config in paths.items():

            common_parameters = config.pop(swagger_constants.PARAMETERS, [])

            for method, method_config in config.items():

                if method in swagger_constants.VALID_METHODS:
                    op = Operation(url=path, method=method, config=method_config)
                    op.add_parameters(common_parameters)
                    self.tasks.append(op.get_task())
                else:
                    logger.warning("Incorrect method - %s %s", method, method_config)


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


class LocustFileConfig:

    def __init__(self, task_set):
        self.task_set = task_set

        self.imports = ["from locust import HttpLocust, TaskSet, task"]
        self.global_vars = []

    def get_imports(self):
        return "\n".join(self.imports)

    def get_global_vars(self):
        return "\n".join(self.global_vars) if self.global_vars else ""

    def get_task_set(self):
        return self.task_set.convert()

    def convert(self):
        file_components = ["{imports}", "{declarations}", "{task_set}"]
        return "\n\n".join(file_components).format(**utils.StringDict(
            imports=self.get_imports(),
            declarations=self.get_global_vars(),
            task_set=self.task_set.convert(width=1)
        ))


if __name__ == "__main__":
    spec = OpenAPISpec(specs)
    spec.get_tasks()
    tasks = TaskSet(tasks=spec.tasks, tag="User")

    locust_file = LocustFileConfig(tasks)

    print(locust_file.convert())
