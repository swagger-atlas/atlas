from atlas.modules import constants, exceptions, utils
from atlas.modules.transformer import interface, profile_constants
from atlas.modules.helpers import swagger_schema_resolver
from atlas.conf import settings


class Task:
    """
    A single task corresponds to single URL/Method combination function
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

        self.post_check_tasks = []

        self.parse_parameters(open_api_interface.parameters or {})

    def normalize_function_name(self):
        raise NotImplementedError

    def parse_parameters(self, parameters):
        """
        For the Path parameters, add required resources
        For the body parameter, add the definition
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
                raise exceptions.ImproperSwaggerException("Config {} does not have name".format(config))

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
                raise exceptions.ImproperSwaggerException(
                    "Config {} does not have valid parameter type".format(config))

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
                    f"Body Parameter {name} must specify schema. OP ID: {self.open_api_op.func_name}"
                )

    def parse_header_params(self, name, config):
        config = self.schema_resolver.resolve({name: config})
        if config:
            self.headers.append("'{name}': {config}".format(name=name, config=config[name]))

    def parse_url_params(self, name, config, param_type="query"):
        """
        :param name: Parameter name
        :param config: Parameter Configuration
        :param param_type: Type of parameter. Query/Path
        """
        _type = config.get(constants.TYPE)

        if not _type:
            raise exceptions.ImproperSwaggerException("Type not defined for parameter - {}".format(name))

        if _type not in constants.QUERY_TYPES:
            raise exceptions.ImproperSwaggerException("Unsupported type for parameter - {}".format(name))

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
            self.url_params[name] = (param_type, config[name])

    def convert(self, width):
        raise NotImplementedError

    def parse_url_params_for_body(self):
        query_params = []
        path_params = []

        param_map = {
            "query": query_params,
            "path": path_params
        }
        for key, value in self.url_params.items():
            param_str = "'{name}': {config}".format(name=key, config=value[1])
            param_map[value[0]].append(param_str)

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

    def get_delete_resource(self) -> str:
        """
        Find the resource which needs to be deleted
        We will assume that in URL, last path params represent the resource to be deleted

        If needed, this can be later revisited and we can see how to handle cascading or multiple deletes
        """

        url_paths = self.open_api_op.url.split("/")
        param = ""

        for component in reversed(url_paths):
            if component.startswith("{") and component.endswith("}"):
                param = component[1:-1]     # Strip leading and trailing curly braces
                break

        return param

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
    Task Set is collection of tasks
    """

    def __init__(self, tasks, scenarios=None):
        self.tasks = tasks
        self.scenarios = self.set_scenarios(scenarios)

    def set_scenarios(self, scenarios):
        """
        Make sure default is appended in scenarios neatly
        """

        scenarios = scenarios or {}

        _default = scenarios.get(profile_constants.DEFAULT_SCENARIO)

        if not _default:
            scenarios[profile_constants.DEFAULT_SCENARIO] = [_task.open_api_op.op_id for _task in self.tasks]

        return scenarios

    def convert(self, width):
        raise NotImplementedError
