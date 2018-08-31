from modules.transformer import open_api_models, open_api_reader
from modules.transformer.base import transformer
from modules.transformer.k6 import models as k6_models
from settings.conf import settings


class K6FileConfig(transformer.FileConfig):

    OUT_FILE = settings.K6_FILE

    @staticmethod
    def get_imports():
        imports = [
            "import http from 'k6/http'",
        ]
        return "\n".join(imports)

    @staticmethod
    def get_global_vars():
        statements = [
            "const baseURL = '{}';".format(settings.HOST_URL)
        ]
        return "\n".join(statements)


if __name__ == "__main__":
    in_file = ""
    spec = open_api_models.OpenAPISpec(open_api_reader.SpecsFile(in_file).file_load())
    spec.get_tasks(k6_models.Task)

    _task_set = k6_models.TaskSet(tasks=spec.tasks, tag="User")

    locust_config = K6FileConfig(_task_set, in_file)
    locust_config.write_to_file()
