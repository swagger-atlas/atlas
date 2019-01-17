from collections import OrderedDict
import logging

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

    def add_to_interface(self, op_interface):

        op_interface.func_name = self.config.get(swagger_constants.OPERATION)
        self.add_parameters(self.config.get(swagger_constants.PARAMETERS, []))
        op_interface.parameters = self.parameters
        op_interface.tags = self.config.get(swagger_constants.TAGS, [])
        op_interface.responses = self.config.get(swagger_constants.RESPONSES, {})
        op_interface.dependent_resources = self.config.get(swagger_constants.DEPENDENT_RESOURCES, set())
        return op_interface


class OpenAPISpec:

    def __init__(self, spec):
        self.spec = spec

        self.paths = OrderedDict()
        self.interfaces = []

    def get_interfaces(self):

        paths = self.spec.get(swagger_constants.PATHS, {})

        # Pre-compile Regex to make matching blazing fast
        exclude_urls = set(getattr(settings, "EXCLUDE_URLS", []))

        global_consume = self.spec.get(swagger_constants.CONSUMES, [])

        for path, config in paths.items():

            common_parameters = config.pop(swagger_constants.PARAMETERS, [])

            for method, method_config in config.items():

                # Ignore Exclude URLs
                op_key = f"{method.upper()} {path}"
                if op_key in exclude_urls:
                    continue

                op_interface = interface.OpenAPITaskInterface()
                op_interface.method = method
                op_interface.url = path
                consumes = method_config.get(swagger_constants.CONSUMES, [])
                consumes.extend(global_consume)
                op_interface.consumes = consumes

                operation = Operation(config=method_config, specs=self.spec)
                operation.add_parameters(common_parameters)

                self.interfaces.append(operation.add_to_interface(op_interface))
