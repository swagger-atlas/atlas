from atlas.modules.commands.base import CommandError
from atlas.modules.transformer.commands.base import TransformerBaseCommand
from atlas.modules.transformer.artillery import (
    models as artillery_models,
    transformer as artillery_transformer,
    yaml_to_js
)
from atlas.modules.transformer.locust import models as locust_models, transformer as locust_transformer
from atlas.modules.transformer import open_api_models, open_api_reader
from atlas.modules.transformer.ordering import ordering


TASK = "task"
TASK_SET = "task_set"
FILE_CONFIG = "file_config"

CONVERTER_MAP = {
    "artillery": {
        TASK: artillery_models.Task,
        TASK_SET: artillery_models.TaskSet,
        FILE_CONFIG: artillery_transformer.ArtilleryFileConfig
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

        order = ordering.Ordering(spec, open_api.interfaces)
        sorted_interfaces = order.order()

        tasks = [load_conf[TASK](interface, spec) for interface in sorted_interfaces]

        _task_set = load_conf[TASK_SET](tasks=tasks, tag="User")

        config = load_conf[FILE_CONFIG](_task_set, spec)
        config.write_to_file()

        if load_conf_type == "artillery":
            js_converter = yaml_to_js.Converter()
            js_converter.convert()
