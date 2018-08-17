from io import open
import json
import os

import six
import yaml

from scripts import (
    constants,
    exceptions,
    locust_models,
    spec_models,
    utils,
)
from settings.conf import settings


class LocustFileConfig:

    def __init__(self, task_set):
        self.task_set = task_set

        self.imports = [
            "from locust import HttpLocust, TaskSet, task",
            "from scripts import spec_converter, spec_models",
            "from scripts.resources.decorators import fetch, body, formatted_url, header"
        ]

    def get_imports(self):
        return "\n".join(self.imports)

    @staticmethod
    def declare_spec_file():
        statements = [
            "specs_file = spec_converter.SpecsFile('{inp}')".format(inp=input_file),
            "spec_instance = spec_models.OpenAPISpec(specs_file.file_load())"
        ]
        return "\n".join(statements)

    def convert(self):
        file_components = ["{imports}", "{spec}", "{task_set}"]
        return "\n\n\n".join(file_components).format(**utils.StringDict(
            imports=self.get_imports(),
            spec=self.declare_spec_file(),
            task_set=self.task_set.convert(width=1)
        ))

    def write_to_file(self, file_name, file_path=None):
        file_path = file_path or "locust_config"
        _path = os.path.join(settings.BASE_DIR, file_path)
        _file = os.path.join(_path, file_name)

        with open(_file, 'w') as write_file:
            write_file.write(self.convert() + "\n") # EOF New line append


class SpecsFile:

    CONVERTER = {
        constants.JSON: json.load,
        constants.YAML: yaml.safe_load
    }

    def __init__(self, spec_file, spec_path=None, converter=None):
        """
        :param spec_file: Specification File Name
        :param spec_path: Specification File Path. Leave Blank to use default path in specs/ folder
        :param converter: Which converter to use (JSON or YAML). Leave Null to let converter identify on its own
        """

        self.spec_path = spec_path or "specs"
        self.spec_file = spec_file
        self.converter = converter

        if isinstance(self.converter, six.string_types):
            self.converter = self.converter.lower()

        if self.converter not in {constants.JSON, constants.YAML}:
            self.identify_converter()

    def identify_converter(self):

        if self.spec_file.endswith(constants.JSON):
            self.converter = constants.JSON
        elif self.spec_file.endswith(constants.YAML):
            self.converter = constants.YAML
        else:
            raise exceptions.ImproperSwaggerException("Incorrect extension for {}".format(self.spec_file))

    def file_load(self):
        file_path = os.path.join(settings.BASE_DIR, self.spec_path)
        _file = os.path.join(file_path, self.spec_file)

        with open(_file) as open_api_file:
            ret_stream = self.CONVERTER[self.converter](open_api_file)

        return ret_stream


if __name__ == "__main__":
    input_file = "header_params.yaml"
    specs_file = SpecsFile(input_file)
    spec = spec_models.OpenAPISpec(specs_file.file_load())
    spec.get_tasks()
    tasks = locust_models.TaskSet(tasks=spec.tasks, tag="User")

    locust_file = LocustFileConfig(tasks)

    locust_file.write_to_file("header.py")
