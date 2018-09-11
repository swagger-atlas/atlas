import random
import string

from atlas.modules import constants, exceptions
from atlas.modules.transformer import data_config, interface
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

        self.swagger_operation_id = open_api_interface.func_name
        self.func_name = self.normalize_function_name()
        self.method = open_api_interface.method
        self.url = open_api_interface.url

        self.data_config = data_config.DataConfig(spec or {})

        self.data_body = dict()
        self.url_params = dict()

        self.headers = []

        self.parse_parameters(open_api_interface.parameters or {})

    def normalize_function_name(self):
        raise NotImplementedError

    def parse_parameters(self, parameters):
        """
        For the Path parameters, add required resources
        For the body parameter, add the definition
        """

        for config in parameters.values():
            in_ = config.get(constants.IN_)

            if not in_:
                raise exceptions.ImproperSwaggerException("In is required field for OpenAPI Parameter")

            name = config.get(constants.PARAMETER_NAME)

            if not name:
                raise exceptions.ImproperSwaggerException("Config {} does not have name".format(config))

            if in_ == constants.PATH_PARAM:
                self.parse_url_params(name, config, param_type="path")

            elif in_ == constants.BODY_PARAM:
                schema = config.get(constants.SCHEMA)
                if not schema:
                    raise exceptions.ImproperSwaggerException("Body Parameter must specify schema")
                self.data_body = schema

            elif in_ == constants.QUERY_PARAM:
                self.parse_url_params(name, config)

            elif in_ == constants.FORM_PARAM:
                self.data_body[name] = config

            elif in_ == constants.HEADER_PARAM:
                self.parse_header_params(name, config)

            else:
                raise exceptions.ImproperSwaggerException(
                    "Config {} does not have valid parameter type".format(config))

        self.data_body = self.data_config.generate(self.data_body)

    def parse_header_params(self, name, config):
        config = self.data_config.generate({name: config})
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

        config = self.data_config.generate({name: config})

        if config:
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


class TaskSet:
    """
    Task Set is collection of tasks
    """

    def __init__(self, tasks, tag=None):
        self.tag = tag or ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.tasks = tasks

    def convert(self, width):
        raise NotImplementedError
