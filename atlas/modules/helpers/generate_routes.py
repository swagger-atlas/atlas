import os
import re

from atlas.modules import constants, utils
from atlas.conf import settings


class GenerateRoutes:

    def __init__(self, spec):
        self.spec = spec

    def get_routes(self):

        routes = []

        paths = self.spec.get(constants.PATHS, {})
        for path, config in paths.items():
            for method in config.keys():
                if method in constants.VALID_METHODS:
                    # Ignore Exclude URLs
                    op_key = f"{method.upper()} {path}"
                    identifier = config.get(constants.OPERATION, utils.operation_id_name(path, method))
                    identifier = re.sub(r'[.-]', '_', identifier)
                    routes.append(f"{identifier.upper()} = '{op_key}'")

        return "\n".join(routes)

    def write_to_routes(self):

        routes_file = os.path.join(settings.INPUT_FOLDER, settings.ROUTES_FILE)

        with open(routes_file, "w") as file_stream:
            file_stream.write(self.get_routes())
            file_stream.write("\n")
