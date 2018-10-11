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
            "import {{ hook, profile }} from '{path}'".format(
                path=os.path.join(utils.get_project_path(), settings.INPUT_FOLDER, settings.K6_HOOK_FILE)
            ),
            "import {{ Provider }} from '{path}'".format(
                path=os.path.join("atlas", "modules", "data_provider", "k6", "providers.js")
            ),
            "import * as settings from 'js_libs/settings.js'"
        ]
        return "\n".join(imports)

    @staticmethod
    def get_global_vars():

        global_statements = [
            f"const baseURL = '{settings.HOST_URL}';",
            "profile.setUp();",
            "let provider;",
            "let defaultHeaders = profile.headers;"
        ]

        setup_template = [
            "export function setup() {",
            "{w}http.get(settings.REDIS_SERVER_URL + '/flushdb');".format(w=" " * 4),
            "{w}new Provider(profile.profileName);".format(w=" "*4),
            "}"
        ]

        statements = [
            "\n".join(global_statements),
            "\n",
            "\n".join(setup_template),
        ]

        return "\n".join(statements)
