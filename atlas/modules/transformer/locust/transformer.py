from atlas.modules.transformer.base import transformer
from atlas.conf import settings


class LocustFileConfig(transformer.FileConfig):

    OUT_FILE = settings.LOCUST_FILE

    @staticmethod
    def get_imports():
        imports = [
            "from locust import HttpLocust, TaskSet, task",
            "from atlas.modules.data_provider.locust.providers import Provider",
            "from {path}.{hooks} import LocustHook".format(
                path=settings.INPUT_FOLDER, hooks=settings.LOCUST_HOOK_FILE[:-len(".py")])
        ]
        return "\n".join(imports)
