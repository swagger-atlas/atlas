import os
import re

from atlas.modules import constants, utils
from atlas.conf import settings


class GenerateRoutes:
    """
    Parse the Swagger file and generate routes along with OP_KEYS for them
    """

    def __init__(self, spec):
        """
        :param spec: Swagger API Specification
        """
        self.spec = spec

    def get_routes(self):
        """
        Parse the Swagger file, and collects all routes
        :return:
            Array<String> where each string is "route = OP_KEY" format
        """

        routes = []

        paths = self.spec.get(constants.PATHS, {})
        for path, config in paths.items():
            for method in config.keys():
                if method in constants.VALID_METHODS:
                    # Ignore Exclude URLs
                    op_key = f"{method.upper()} {path}"
                    identifier = re.sub(r'[.-]', '_', utils.operation_id_name(path, method))
                    routes.append(f"{identifier.upper()} = '{op_key}'")

        return "\n".join(routes)

    def write_to_routes(self):
        """
        Create (if required) and write to Routes file
        """

        routes_file = os.path.join(settings.INPUT_FOLDER, settings.ROUTES_FILE)

        with open(routes_file, "w") as file_stream:
            file_stream.write(self.get_routes())
            file_stream.write("\n")
