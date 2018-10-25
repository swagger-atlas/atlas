import os

from atlas.modules import utils, mixins
from atlas.modules.transformer.base import transformer
from atlas.conf import settings


class K6FileConfig(mixins.YAMLReadWriteMixin, transformer.FileConfig):

    OUT_FILE = settings.ARTILLERY_FILE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.yaml_config = {}

    def get_imports(self):
        imports = [
            "import _ from 'js_libs/lodash.js'",
            "import {{ hook, profile }} from '{path}'".format(
                path=os.path.join(utils.get_project_path(), settings.INPUT_FOLDER, settings.K6_HOOK_FILE)
            ),
            "import {{ Provider, ResponseDataParser }} from '{path}'".format(
                path=os.path.join("atlas", "modules", "data_provider", "k6", "providers.js")
            ),
            "import * as settings from 'js_libs/settings.js'"
        ]
        return "\n".join(imports)

    def get_global_vars(self):

        return "\n".join([
            "profile.setUp();",
            "let provider, respDataParser;",
            "let defaultHeaders = profile.headers;",
        ])

    def set_yaml_config(self):
        # TODO: Default headers, move hook codes appropriate positions
        self.yaml_config = {
            "config": {
                "target": self.get_swagger_url(),
                "processor": f"./{self.OUT_FILE}",
                "phases": [
                    {
                        "duration": 1,
                        "arrivalCount": 1
                    }
                ]
            },
            "scenarios": [
                self.task_set.yaml_flow
            ]
        }

    def write_to_file(self, file_name=None):
        super().write_to_file(file_name)

        self.set_yaml_config()
        self.write_file_to_output(settings.ARTILLERY_YAML, self.yaml_config, append_mode=False)
