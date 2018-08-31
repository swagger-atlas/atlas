from modules.transformer.base import transformer
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
    def global_vars():
        statements = [
            "const baseURL = '{}'".format(settings.HOST_URL)
        ]
        return "\n".join(statements)
