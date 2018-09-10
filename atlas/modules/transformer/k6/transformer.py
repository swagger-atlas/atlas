import os

from atlas.modules import utils
from atlas.modules.transformer.base import transformer
from atlas.conf import settings


class K6FileConfig(transformer.FileConfig):

    OUT_FILE = settings.K6_FILE

    @staticmethod
    def get_imports():
        imports = [
            "import http from 'k6/http'",
            "import { check, group } from 'k6'",
            "import _ from 'js_libs/lodash.js'",
            "import {{ hook, defaultHeaders }} from '{path}'".format(
                path=os.path.join(utils.get_project_path(), settings.INPUT_FOLDER, settings.K6_HOOK_FILE)
            ),
            "import {{ Provider }} from '{path}'".format(
                path=os.path.join("modules", "data_provider", "k6", "providers.js")
            )
        ]
        return "\n".join(imports)

    @staticmethod
    def get_global_vars():
        statements = [
            "const baseURL = '{}';".format(settings.HOST_URL),
            "const provider = new Provider(hook.profile);"
        ]
        return "\n".join(statements)
