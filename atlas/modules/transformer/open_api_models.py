import logging
from collections import OrderedDict

from atlas.modules import (
    constants as swagger_constants,
    exceptions
)
from atlas.modules.transformer import interface
from atlas.conf import settings

logger = logging.getLogger(__name__)


class Operation:
    """
    Define an OpenAPI Specific Operation
    """

    def __init__(self, config):

        self.config = config
        self.parameters = OrderedDict()

    def add_parameters(self, parameters):

        # ASSUMPTION: We will assume that our parameters are not defined by refs
        # This seems a valid assumption considering that none of Swagger Generators do that right now

        for parameter in parameters:
            name = parameter.get(swagger_constants.PARAMETER_NAME, None)

            if not name:
                raise exceptions.ImproperSwaggerException(
                    "Parameter configuration does not have name - {}".format(parameter)
                )

            self.parameters[name] = parameter

    def add_to_interface(self, op_interface):

        op_interface.func_name = self.config.get(swagger_constants.OPERATION)
        self.add_parameters(self.config.get(swagger_constants.PARAMETERS, []))
        op_interface.parameters = self.parameters
        op_interface.tags = self.config.get(swagger_constants.TAGS, [])
        responses = self.config.get(swagger_constants.RESPONSES, {})
        op_interface.responses = {
            key: value for key, value in responses.items() if key in swagger_constants.VALID_RESPONSES
        }
        return op_interface


class OpenAPISpec:

    def __init__(self, spec):
        self.spec = spec

        self.paths = OrderedDict()
        self.interfaces = []

    def get_interfaces(self):

        paths = self.spec.get(swagger_constants.PATHS, {})

        for path, config in paths.items():

            # We do not include these URLs in our Load Test
            if path in getattr(settings, "EXCLUDE_URLS", []):
                continue

            common_parameters = config.pop(swagger_constants.PARAMETERS, [])

            for method, method_config in config.items():
                op_interface = interface.OpenAPITaskInterface()
                op_interface.method = method
                op_interface.url = path

                operation = Operation(config=method_config)
                operation.add_parameters(common_parameters)
                self.interfaces.append(operation.add_to_interface(op_interface))
