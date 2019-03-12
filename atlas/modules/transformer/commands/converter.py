from atlas.conf import settings
from atlas.modules.commands.base import CommandError
from atlas.modules.helpers import open_api_reader
from atlas.modules.transformer.commands.base import TransformerBaseCommand
from atlas.modules.transformer.artillery import (
    models as artillery_models,
    transformer as artillery_transformer,
    yaml_to_js
)
from atlas.modules.transformer import open_api_models
from atlas.modules.transformer.ordering import ordering


TASK = "task"
TASK_SET = "task_set"
FILE_CONFIG = "file_config"

CONVERTER_MAP = {
    "artillery": {
        TASK: artillery_models.Task,
        TASK_SET: artillery_models.TaskSet,
        FILE_CONFIG: artillery_transformer.ArtilleryFileConfig
    }
}


class Converter(TransformerBaseCommand):
    """
    Convert Swagger file to configuration file
    """

    VALID_CONVERTERS = ", ".join(CONVERTER_MAP.keys())

    help = "Converts Swagger file to configuration file which could be fed into Load Tester"

    def handle(self, **options):
        """
        Operation Order is:
        1. Load Swagger
        2. Convert it into interfaces which are then used by sub-sequent operations instead of working on raw swagger
        3. Decide the order of operations in which APIs should be hit
        4. For each API, transform their swagger configuration to load test configuration
        5. Collate these conversions with scenarios if available
        6. Transform the final generated code snippet into working code/config, and write it to correct file
        """

        load_conf_type = options.pop("type")

        load_conf = CONVERTER_MAP.get(load_conf_type)

        if not load_conf:
            raise CommandError(f"Invalid Load Testing Type. Valid types are: {self.VALID_CONVERTERS}")

        spec = open_api_reader.SpecsFile().file_load()
        open_api = open_api_models.OpenAPISpec(spec)
        open_api.get_interfaces()

        order = ordering.Ordering(spec, open_api.interfaces)
        sorted_interfaces = order.order()

        scenarios = settings.LOAD_TEST_SCENARIOS

        tasks = [load_conf[TASK](interface, spec) for interface in sorted_interfaces]

        _task_set = load_conf[TASK_SET](tasks=tasks, scenarios=scenarios)

        config = load_conf[FILE_CONFIG](_task_set, spec)
        config.write_to_file()

        if load_conf_type == "artillery":
            js_converter = yaml_to_js.Converter()
            js_converter.convert()
