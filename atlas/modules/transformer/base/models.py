from collections import namedtuple

from atlas.modules import constants, exceptions, utils
from atlas.modules.transformer import interface, profile_constants
from atlas.modules.helpers import swagger_schema_resolver
from atlas.conf import settings


# Swagger Field Name and Resource it maps to
ResourceFieldMap = namedtuple('ResourceFieldMap', [constants.RESOURCE, 'field'])


class Task:
    """
    Responsibility of the task is to take single Operation (URL + Method) and output its load test configuration
    Convert() is the entry point for the function, and must be implemented by sub-classes
    Base class implements several of utility methods, and resolve Parameters
    """

    def __init__(self, open_api_interface: interface.OpenAPITaskInterface, spec=None):
        """
        :param open_api_interface: OpenAPI interface for this task
        :param spec: Complete spec definition
        """

        self.open_api_op = open_api_interface
        self.func_name = self.normalize_function_name()

        self.schema_resolver = swagger_schema_resolver.SchemaResolver(spec or {})

        self.data_body = dict()
        self.url_params = dict()

        self.headers = []

        # Contains what all statements/configuration need to occur AfterResponse has been received
        self.post_check_tasks = []

        # If this Operation deletes the resource, we save it.
        # This is necessary, because we might need to roll-back delete operations
        self.delete_url_resource = None

        self.parse_parameters(open_api_interface.parameters or {})

    def normalize_function_name(self):
        raise NotImplementedError

    def parse_parameters(self, parameters):
        """
        This contains the main logic for Parsing Parameters present in the operation.

        Parameters could be of type: URL (Path. Query), Headers, Body (body, form etc).
        For each parameter, we:
            - run basic validations for them
            - process them, and if they are reference, resolve the references
            - run basic checks for them, and save their config in requisite variables
        """

        for config in parameters.values():

            ref = config.get(constants.REF)
            if ref:
                config = utils.resolve_reference(self.schema_resolver.spec, ref)

            in_ = config.get(constants.IN_)

            if not in_:
                raise exceptions.ImproperSwaggerException("In is required field for OpenAPI Parameter")

            name = config.get(constants.PARAMETER_NAME)

            if not name:
                raise exceptions.ImproperSwaggerException(f"Config {config} does not have name")

            if in_ == constants.PATH_PARAM:
                self.parse_url_params(name, config, param_type="path")

            elif in_ == constants.BODY_PARAM:
                self.parse_body_params(name, config)

            elif in_ == constants.QUERY_PARAM:
                self.parse_url_params(name, config)

            elif in_ == constants.FORM_PARAM:
                self.data_body[name] = config

            elif in_ == constants.HEADER_PARAM:
                self.parse_header_params(name, config)

            else:
                raise exceptions.ImproperSwaggerException(f"Config {config} does not have valid parameter type")

        # schema_resolver.resolve() would expand nested references and definitions, and would give nested object
        self.data_body = self.schema_resolver.resolve(self.data_body)

    def parse_body_params(self, name, config):
        schema = config.get(constants.SCHEMA)
        if schema:
            self.data_body = schema
        else:
            # If schema is not there, we want to see if we can safely ignore this before raising error
            required = config.get(constants.REQUIRED, True)
            if required:
                raise exceptions.ImproperSwaggerException(
                    f"Body Parameter {name} must specify schema. OP ID: {self.open_api_op.op_id}"
                )

    def parse_header_params(self, name, config):
        config = self.schema_resolver.resolve({name: config})
        if config:
            self.headers.append(f"'{name}': {config[name]}")

    def parse_url_params(self, name, config, param_type="query"):
        """
        :param name: Parameter name
        :param config: Parameter Configuration
        :param param_type: Type of parameter. Query/Path
        """
        _type = config.get(constants.TYPE)

        if not _type:
            raise exceptions.ImproperSwaggerException(f"Type not defined for parameter - {name}")

        if _type not in constants.URL_TYPES:
            raise exceptions.ImproperSwaggerException(f"Unsupported type for parameter - {name}")

        # Only use query params if strictly required
        is_optional_param = not (settings.HIT_ALL_QUERY_PARAMS or config.get(constants.REQUIRED, False))
        if param_type == "query" and is_optional_param:
            return

        # Special Handling for Page Query Parameters
        if name in settings.POSITIVE_INTEGER_PARAMS:
            config[constants.MINIMUM] = 1

        config = self.schema_resolver.resolve({name: config})

        if config:
            if self.open_api_op.url_end_parameter() == name and self.open_api_op.method == constants.DELETE:
                config[name]["options"] = {"delete": 1}
                # Using 1 instead of true since this avoids Language issues. All languages treat 1 as same
                # However, different languages have different truth values eg: True (Python), true (javascript)
                self.delete_url_resource = ResourceFieldMap(config[name].get(constants.RESOURCE), name)
            self.url_params[name] = (param_type, config[name])

    def convert(self, width):
        raise NotImplementedError

    def parse_url_params_for_body(self) -> (str, str):
        """
        Utility Method.
        It process url_params constructed when parsing parameters, and return query and path string
        """
        query_params = []
        path_params = []

        param_map = {
            "query": query_params,
            "path": path_params
        }
        for key, value in self.url_params.items():
            param_map[value[0]].append(f"'{key}': {value[1]}")

        query_str = "{}"
        path_str = "{}"

        if query_params:
            query_str = "{" + ", ".join(query_params) + "}"

        if path_params:
            path_str = "{" + ", ".join(path_params) + "}"

        return query_str, path_str

    def get_response_properties(self, config):
        properties = (
            self.schema_resolver.resolve_with_read_only_fields(config.get(constants.SCHEMA, {}))
        )
        if properties:
            return properties

        return {}

    def parse_responses(self, responses):
        """
        Resolve the responses.
        """

        return_response = {}

        for status, config in responses.items():

            # Swagger responses are either status code or "default".
            if status == constants.DEFAULT:
                response = self.get_response_properties(config)
                if response:
                    return_response = response
                continue      # No need to do any other checks

            try:
                status_code = int(status)
            except (ValueError, TypeError):
                raise exceptions.ImproperSwaggerException(f"Swagger {responses} status codes must be Integer Strings")
            else:
                # 2xx responses are typically used as indication of valid response
                if 200 <= status_code < 300:
                    # Short-circuit return with first valid response we encountered
                    schema = self.get_response_properties(config)
                    if schema:
                        return schema

        return return_response

    def has_files(self):
        """
        Check if there is going to be file structure
        We only need to iterate over top level since OAS 2 only supports that
        """

        for config in self.data_body.values():
            if isinstance(config, dict) and config.get(constants.TYPE) == constants.FILE:
                return True
        return False


class TaskSet:
    """
    Task Set takes a collection of tasks and give load test configuration which combines them all.
    Subclasses must implement convert
    """

    # List(Task) does not work -- see: https://github.com/python/typing/issues/113
    def __init__(self, tasks: list, scenarios: dict = None):
        """
        :param tasks: Array of Tasks
        :param scenarios: Custom user scenarios.

        If no scenario is present, default scenario will be used which is a collection of all tasks
        """
        self.tasks = tasks
        self.scenarios = self.set_scenarios(scenarios)

    def set_scenarios(self, scenarios):
        """
        Make sure default is added in scenarios correctly
        """

        scenarios = scenarios or {}

        _default = scenarios.get(profile_constants.DEFAULT_SCENARIO)

        if not _default:
            scenarios[profile_constants.DEFAULT_SCENARIO] = [_task.open_api_op.op_id for _task in self.tasks]

        return scenarios

    def convert(self, width):
        raise NotImplementedError
