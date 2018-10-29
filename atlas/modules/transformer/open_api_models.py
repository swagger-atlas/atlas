from collections import OrderedDict
import logging
import re

from atlas.modules import (
    constants as swagger_constants,
    exceptions,
    utils
)
from atlas.modules.transformer import interface
from atlas.conf import settings

logger = logging.getLogger(__name__)


class Operation:
    """
    Define an OpenAPI Specific Operation
    """

    def __init__(self, config, specs=None):

        self.config = config
        self.parameters = OrderedDict()
        self.specs = specs or {}

    def add_parameters(self, parameters):

        for parameter in parameters:

            ref = parameter.get(swagger_constants.REF)
            if ref:
                parameter = utils.resolve_reference(self.specs, ref)

            name = parameter.get(swagger_constants.PARAMETER_NAME, None)

            if not name:
                raise exceptions.ImproperSwaggerException(
                    "Parameter configuration does not have name - {}".format(parameter)
                )

            self.parameters[name] = parameter

    @staticmethod
    def operation_id_name(op_interface) -> str:
        """
        Generate the name for Operation ID

        Logic:
            user/       - (user_create, user_list)
            user/{id}   - (user_read, user_update, user_delete)
            user/{id}/action - (user_action with above logic)
        """

        url_fragments = op_interface.url.split("/")

        op_name_array = [url_element for url_element in url_fragments if not url_element.startswith("{")]

        if op_interface.method == swagger_constants.DELETE:
            op_name_array.append("delete")
        elif url_fragments[-1].startswith("{"):
            op_name_array.append("read" if op_interface.method == swagger_constants.GET else "update")
        else:
            op_name_array.append("list" if op_interface.method == swagger_constants.GET else "create")

        return "_".join(op_name_array)

    def add_to_interface(self, op_interface):

        op_interface.func_name = self.config.get(swagger_constants.OPERATION, self.operation_id_name(op_interface))
        self.add_parameters(self.config.get(swagger_constants.PARAMETERS, []))
        op_interface.parameters = self.parameters
        op_interface.tags = self.config.get(swagger_constants.TAGS, [])
        op_interface.responses = self.config.get(swagger_constants.RESPONSES, {})
        return op_interface


class OpenAPISpec:

    def __init__(self, spec):
        self.spec = spec

        self.paths = OrderedDict()
        self.interfaces = []

    def get_interfaces(self):

        paths = self.spec.get(swagger_constants.PATHS, {})

        # Pre-compile Regex to make matching blazing fast
        exclude_urls = getattr(settings, "EXCLUDE_URLS", [])
        exclude_url_regex = re.compile(r"|".join(url for url in exclude_urls))

        for path, config in paths.items():

            # We do not include these URLs in our Load Test
            if re.search(exclude_url_regex, path):
                continue

            common_parameters = config.pop(swagger_constants.PARAMETERS, [])

            for method, method_config in config.items():
                op_interface = interface.OpenAPITaskInterface()
                op_interface.method = method
                op_interface.url = path

                operation = Operation(config=method_config, specs=self.spec)
                operation.add_parameters(common_parameters)

                self.interfaces.append(operation.add_to_interface(op_interface))
