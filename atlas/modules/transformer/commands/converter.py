from atlas.modules.commands.base import CommandError
from atlas.modules.transformer.commands.base import TransformerBaseCommand
from atlas.modules.transformer.k6 import models as k6_models, transformer as k6_transformer
from atlas.modules.transformer.locust import models as locust_models, transformer as locust_transformer
from atlas.modules.transformer import open_api_models, open_api_reader


TASK = "task"
TASK_SET = "task_set"
FILE_CONFIG = "file_config"

CONVERTER_MAP = {
    "k6": {
        TASK: k6_models.Task,
        TASK_SET: k6_models.TaskSet,
        FILE_CONFIG: k6_transformer.K6FileConfig
    },
    "locust": {
        TASK: locust_models.Task,
        TASK_SET: locust_models.TaskSet,
        FILE_CONFIG: locust_transformer.LocustFileConfig
    }
}


class Converter(TransformerBaseCommand):
    """
    Convert Swagger file to configuration file
    """

    VALID_CONVERTERS = ", ".join(CONVERTER_MAP.keys())

    help = "Converts Swagger file to configuration file which could be fed into Load Tester"

    def handle(self, **options):
        load_conf_type = options.pop("type")

        load_conf = CONVERTER_MAP.get(load_conf_type)

        if not load_conf:
            raise CommandError("Invalid Load Testing Type. Valid types are: {}".format(self.VALID_CONVERTERS))

        spec = open_api_reader.SpecsFile().file_load()
        open_api = open_api_models.OpenAPISpec(spec)
        open_api.get_interfaces()

        tasks = [load_conf[TASK](interface, spec) for interface in open_api.interfaces]

        _task_set = load_conf[TASK_SET](tasks=tasks, tag="User")

        config = load_conf[FILE_CONFIG](_task_set)
        config.write_to_file()
