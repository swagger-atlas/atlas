from modules import utils
from modules.transformer import open_api_models, open_api_reader
from modules.transformer.base import transformer
from modules.transformer.locust import models as locust_models
from settings.conf import settings


class LocustFileConfig(transformer.FileConfig):

    OUT_FILE = settings.LOCUST_FILE

    @staticmethod
    def get_imports():
        imports = [
            "from locust import HttpLocust, TaskSet, task",
            "from modules.data_provider.locust.providers import Provider",
            "from {path}.{hooks} import LocustHook".format(
                path=utils.get_input_project_module(), hooks=settings.LOCUST_HOOK_FILE[:-len(".py")])
        ]
        return "\n".join(imports)


if __name__ == "__main__":
    in_file = ""
    spec = open_api_models.OpenAPISpec(open_api_reader.SpecsFile(in_file).file_load())
    spec.get_tasks(locust_models.Task)

    _task_set = locust_models.TaskSet(tasks=spec.tasks, tag="User")

    locust_config = LocustFileConfig(_task_set, in_file)
    locust_config.write_to_file()
