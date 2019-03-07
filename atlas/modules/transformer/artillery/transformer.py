from atlas.modules import mixins
from atlas.modules.transformer.base import transformer
from atlas.conf import settings
from atlas.modules.transformer.artillery import templates


class ArtilleryFileConfig(mixins.YAMLReadWriteMixin, transformer.FileConfig):
    """
    Takes a models.TaskSet object, and transforms its snippets into final JS and YAML file and write them as required

    INPUT:
        Swagger Specs
        Task Set

    OUTPUT:
        Write YAML file containing complete YAML Configuration
        Write Processor file containing complete JS file

    This class is responsible for calling TaskSet.convert and triggering entire conversion
    """

    OUT_FILE = settings.ARTILLERY_FILE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.yaml_config = {}

    def get_imports(self) -> str:
        """
        Processor File Import statements
        """

        imports = [
            "_ = require('lodash');",
            "stream = require('stream');",
            f"const hookRegister = require('./{settings.ARTILLERY_HOOK_FILE}').hookRegister;",
            f"hook = require('./{settings.ARTILLERY_LIB_FOLDER}/hooks').hook;",
            f"utils = require('./{settings.ARTILLERY_LIB_FOLDER}/providers');",
            f"settings = require('./{settings.ARTILLERY_LIB_FOLDER}/settings');",
            f"StatsCollector = require('./{settings.ARTILLERY_LIB_FOLDER}/statsCollector').StatsCollector;",
            f"profiles = require('./{settings.ARTILLERY_LIB_FOLDER}/profiles').profiles;",
            f"influx = require('./{settings.ARTILLERY_LIB_FOLDER}/influx').client;",
        ]
        return "\n".join(imports)

    def get_global_vars(self) -> str:
        """
        Processor File Global statements
        """
        return templates.GLOBAL_STATEMENTS

    def set_yaml_config(self) -> None:
        """
        Construct Artillery YAML configuration
        """

        # LT-248: We can pick Artillery Phase configuration from conf file
        self.yaml_config = {
            "config": {
                "target": self.get_swagger_url(),
                "processor": f"./{self.OUT_FILE}",
                "phases": [
                    {
                        "duration": settings.DURATION or 1,
                        "arrivalRate": settings.SPAWN_RATE or 1
                    }
                ]
            },
            "scenarios": self.task_set.yaml_flow
        }

    def write_to_file(self, file_name=None, sub_path=None) -> None:
        """
        Write to YAML and JS files the final constructed configurations
        """
        super().write_to_file(file_name, settings.ARTILLERY_FOLDER)

        self.set_yaml_config()
        self.write_file_to_output(
            settings.ARTILLERY_YAML, self.yaml_config, append_mode=False, project_sub_folder=settings.ARTILLERY_FOLDER
        )
