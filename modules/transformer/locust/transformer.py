from io import open
import os

from modules import utils
from modules.transformer import open_api_models, open_api_reader
from modules.transformer.locust import models as locust_models
from settings.conf import settings


class LocustFileConfig:

    def __init__(self, task_set, specs_file=None):
        self.task_set = task_set
        self.spec_file = specs_file or settings.SWAGGER_FILE

        self.imports = [
            "from locust import HttpLocust, TaskSet, task",
            "from modules.data_provider.locust.mapper import DataMapper",
            "from {path}.{hooks} import LocustHook".format(
                path=utils.get_input_project_module(), hooks=settings.LOCUST_HOOK_FILE[:-len(".py")])
        ]

    def get_imports(self):
        return "\n".join(self.imports)

    def convert(self):
        file_components = ["{imports}", "{task_set}"]
        return "\n\n\n".join(file_components).format(**utils.StringDict(
            imports=self.get_imports(),
            task_set=self.task_set.convert(width=1)
        ))

    def write_to_file(self, file_name=None):
        file_name = file_name or settings.LOCUST_FILE
        _file = os.path.join(utils.get_project_path(), settings.OUTPUT_FOLDER, file_name)

        with open(_file, 'w') as write_file:
            write_file.write(self.convert() + "\n")  # Append EOF New line


if __name__ == "__main__":
    in_file = ""
    spec = open_api_models.OpenAPISpec(open_api_reader.SpecsFile(in_file).file_load())
    spec.get_tasks(locust_models.Task)

    _task_set = locust_models.TaskSet(tasks=spec.tasks, tag="User")

    locust_config = LocustFileConfig(_task_set, in_file)
    locust_config.write_to_file()
