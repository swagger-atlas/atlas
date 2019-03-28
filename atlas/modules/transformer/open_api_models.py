from collections import defaultdict, OrderedDict
import logging

from atlas.modules import (
    constants as swagger_constants,
    exceptions,
    utils
)
from atlas.modules.helpers import open_api
from atlas.modules.transformer import interface
from atlas.conf import settings

logger = logging.getLogger(__name__)

RESOURCES = "resources"
DEF = "_definitions"
REFERENCES = "references"


class Response:

    def __init__(self, specs=None):
        self.specs = specs or {}

        self.definitions = {}

    def get_properties(self, config):
        """
        Find Properties by recursively reducing array and objects
        """

        _type = config.get(swagger_constants.TYPE)

        if _type == swagger_constants.ARRAY:
            return self.get_properties(config.get(swagger_constants.ITEMS, {}))

        if _type == swagger_constants.OBJECT:
            return config.get(swagger_constants.PROPERTIES, {})

        return config

    @staticmethod
    def get_definition_ref(config):
        # Check for ref first
        ref = config.get(swagger_constants.REF)
        if ref:
            ref = utils.get_ref_name(ref).lower()
        return ref

    def resolve_definitions(self):
        definitions = self.specs.get(swagger_constants.DEFINITIONS, {})
        self.parse_definitions(definitions)

        for name in definitions.keys():
            self.definitions[name.lower()][RESOURCES] = self.resolve_nested_definition(name.lower())

    def parse_definitions(self, definitions):

        for name, config in definitions.items():
            name = name.lower()
            self.definitions[name] = defaultdict(set)
            self.definitions[name][REFERENCES].add(name)

            # Adding config as default all_of reduces number of conditionals required
            # It should NOT be interpreted as that config is actually part of all_of
            all_of_config = config.get(swagger_constants.ALL_OF, [config])
            for element in all_of_config:
                self.parse_field_config(name, element)

    def parse_field_config(self, name, field_config):

        field_config = self.get_properties(field_config)

        resource = field_config.get(swagger_constants.RESOURCE)
        if resource:
            self.definitions[name][RESOURCES].add(resource)

        ref = self.get_definition_ref(field_config)
        if ref:
            self.definitions[name][DEF].add(ref)

    def resolve_nested_definition(self, definition):

        # Can speed this up by marking elements which are already processed
        # Note: Any such optimization should be reflected in calling/parent functions also
        config = self.definitions.get(definition)

        while config.get(DEF):
            new_definition = config[DEF].pop()
            self.definitions[definition][REFERENCES].add(new_definition)
            config[RESOURCES].update(self.resolve_nested_definition(new_definition))

        return config[RESOURCES]


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
    def get_schema_refs(config):
        schema = open_api.Schema(config.get(swagger_constants.SCHEMA, {}))
        return [utils.get_ref_name(ref).lower() for ref in schema.get_all_refs()]

    def add_resource_producers(self, operation, resp_mapping):

        for response in operation.responses.values():

            # Assumption: PUT/PATCH/DELETE Method do not add any new resource
            if operation.method in {swagger_constants.DELETE, swagger_constants.PATCH, swagger_constants.PUT}:
                continue

            response_refs = self.get_schema_refs(response)

            for ref in response_refs:
                config = resp_mapping.get(ref, {})
                operation.resource_producers = config.get(RESOURCES, set())
                operation.producer_references = config.get(REFERENCES, set())

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

        self.responses = Response(spec)

        self.paths = OrderedDict()
        self.interfaces = []

    def get_interfaces(self):

        self.responses.resolve_definitions()

        paths = self.spec.get(swagger_constants.PATHS, {})
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

                op_interface = operation.add_to_interface(op_interface)
                operation.add_resource_producers(op_interface, self.responses.definitions)

                self.interfaces.append(op_interface)
