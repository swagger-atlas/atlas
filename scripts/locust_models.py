import logging
from io import open
import os
import random
import re
import string

from scripts import (
    constants,
    exceptions,
    utils
)
from settings.conf import settings

logger = logging.getLogger(__name__)


class Task:
    """
    Define a single Task of Locust File
    """

    def __init__(self, func_name, method, url, parameters=None, spec=None):
        """
        :param func_name: Function name to be defined in Locust Config File
        :param method: Request Method
        :param url: URL to which this method corresponds
        :param parameters: OpenAPI Parameters
        :param spec: Complete spec definition
        """

        self.func_name = self.normalize_function_name(func_name)
        self.method = method
        self.url = url
        self.parameters = parameters or {}

        self.spec = spec or {}

        self.decorators = ["@task(1)"]
        self.custom_url = False

        self.data_body = dict()
        self.query_params = dict()

        self.headers = []

        self.parse_parameters()

    @staticmethod
    def normalize_function_name(fun_name):
        """
        Convert - into _
        """

        return re.sub("-", "_", fun_name)

    def get_function_parameters(self):
        parameter_list = ["self"]
        if self.custom_url:
            parameter_list.append("format_url")
        parameter_list.append("**kwargs")
        return ", ".join(parameter_list)

    def get_function_declaration(self, width):
        return "{decorators}\n{w}def {name}({parameters}):".format(
            **utils.StringDict(
                decorators=self.get_decorators(width), name=self.func_name, parameters=self.get_function_parameters(),
                w=' ' * width * 4)
        )

    def parse_parameters(self):
        """
        For the Path parameters, add required resources
        For the body parameter, add the definition
        """

        form_data = []

        for config in self.parameters.values():
            in_ = config.get(constants.IN_)

            if not in_:
                raise exceptions.ImproperSwaggerException("In is required field for OpenAPI Parameter")

            if in_ == constants.PATH_PARAM:
                self.parse_path_params(config)

            elif in_ == constants.BODY_PARAM:
                schema = config.get(constants.SCHEMA)

                if not schema:
                    raise exceptions.ImproperSwaggerException("Body Parameter must specify schema")

                self.parse_schema(schema)

            elif in_ == constants.QUERY_PARAM:
                self.construct_query_parameter(config)

            elif in_ == constants.FORM_PARAM:
                form_data.append(config)

            elif in_ == constants.HEADER_PARAM:
                self.parse_header_params(config)

            else:
                raise exceptions.ImproperSwaggerException("Config {} does not have valid parameter type".format(config))

        if form_data:
            self.data_body[self.func_name] = form_data

    def parse_path_params(self, config):
        resource = config.get(constants.RESOURCE)

        if resource:
            self.decorators.append(self.create_resource_decorator(resource))
            self.custom_url = True
        else:
            # if we do not have resource, we still need to make a valid URL
            self.construct_query_parameter(config, param_type="path")

    def parse_header_params(self, config):
        name = config.get(constants.PARAMETER_NAME)
        if not name:
            raise exceptions.ImproperSwaggerException("Config {} does not have name".format(config))
        self.headers.append("'{name}': {config}".format(name=name, config=config))

    def construct_query_parameter(self, query_config, param_type="query"):
        """
        :param query_config: Parameter Configuration
        :param param_type: Type of parameter. Query/Path
        """
        name = query_config[constants.PARAMETER_NAME]
        _type = query_config.get(constants.TYPE)

        if not _type:
            raise exceptions.ImproperSwaggerException("Type not defined for parameter - {}".format(name))

        if _type not in constants.QUERY_TYPES:
            raise exceptions.ImproperSwaggerException("Unsupported type for parameter - {}".format(name))

        self.query_params[name] = (param_type, query_config)

    def parse_schema(self, schema_config):
        """
        Parse the schema for request bodies
        """

        ref = schema_config.get(constants.REF)

        if ref:
            schema_config = utils.resolve_reference(self.spec, ref)

        schema_type = schema_config.get(constants.TYPE)

        if not schema_type:
            raise exceptions.ImproperSwaggerException("Request body must either define reference or Data Type")

        if schema_type != constants.OBJECT:
            schema_config[constants.PROPERTIES] = {"dummy": schema_type}

        properties = schema_config.get(constants.PROPERTIES)

        if not properties:
            raise exceptions.ImproperSwaggerException("An Object must define properties")

        self.data_body[self.func_name] = properties

    def create_resource_decorator(self, resource):
        return "@{res_method}(resource='{resource}', url='{url}')".format(**utils.StringDict(
            res_method=constants.RESOURCE_MAPPING.get(self.method, constants.FETCH),
            resource=resource, url=self.url
        ))

    def get_client_parameters(self):
        """
        Parameters for calling Request method
        """
        parameter_list = ["url"]
        if self.data_body:
            parameter_list.append("data=body(body_config, spec_instance.spec)")
        if self.query_params:
            parameter_list.append("params=path_params")
        if self.headers:
            parameter_list.append("headers=header(header_config)")
        return ", ".join(parameter_list)

    def construct_body_variables(self):
        body_definition = []

        for value in self.data_body.values():
            body_definition.append("body_config = {config}".format(config=value))

        query_params = []
        path_params = []

        param_map = {
            "query": query_params,
            "path": path_params
        }
        for key, value in self.query_params.items():
            param_str = "'{name}': {config}".format(name=key, config=value[1])
            param_map[value[0]].append(param_str)

        query_str = "{}"
        path_str = "{}"
        url_str = "url = {}".format("format_url" if self.custom_url else "'{}'".format(self.url))

        body_definition.append(url_str)

        if query_params:
            query_str = "{" + ", ".join(query_params) + "}"

        if path_params:
            path_str = "{" + ", ".join(path_params) + "}"

        if query_str != "{}" or path_str != "{}":
            # If one if present, we need to append both
            body_definition.append("query_config = {q}".format_map(utils.StringDict(q=query_str)))
            body_definition.append("path_config = {p}".format_map(utils.StringDict(p=path_str)))

            # Also get Path Parameters
            body_definition.append("url, path_params = formatted_url(url, query_config, path_config)")

        if self.headers:
            body_definition.append("header_config = {{{}}}".format(", ".join(self.headers)))

        return body_definition

    def get_function_definition(self, width):

        body_definition = self.construct_body_variables()

        body_definition.append("self.client.{method}({params})".format_map(
            utils.StringDict(method=self.method, params=self.get_client_parameters())
        ))

        join_str = "\n{w}".format(w=' ' * width * 4)
        return join_str.join(body_definition)

    def get_decorators(self, width):
        return "\n{w}".join(self.decorators).format_map(utils.StringDict(w=' ' * width * 4))

    def convert(self, width):
        """
        Convert the task to function
        """

        components = ["{declaration}", "{definition}"]
        return "\n{w}".join(components).format(**utils.StringDict(
            declaration=self.get_function_declaration(width - 1), definition=self.get_function_definition(width),
            w=' ' * width * 4
        ))


class TaskSet:

    def __init__(self, tasks, tag=None):
        self.tag = tag or ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.tasks = tasks

    def generate_tasks(self, width):
        join_string = "\n\n{w}".format(w=' ' * width * 4)
        return join_string.join([_task.convert(width + 1) for _task in self.tasks])

    @staticmethod
    def generate_on_start(width):
        return "def on_start(self):\n{w}self.login()".format(w=' ' * (width + 1) * 4)

    @property
    def task_set_name(self):
        return self.tag + "Behaviour"

    @staticmethod
    def add_hooks(width):
        hook_file = os.path.join(settings.BASE_DIR, settings.PROJECT_FOLDER_NAME,
                                 settings.PROJECT_NAME, settings.LOCUST_HOOK_FILE)

        with open(hook_file, "r") as hook_stream:
            hooks_statements = [line for line in hook_stream]

        join_str = "{w}".format(w=' ' * width * 4)
        return join_str.join(hooks_statements)

    def get_behaviour(self, width):
        join_str = "\n\n{w}".format(w=' ' * width * 4)
        behaviour_components = [
            "class {klass}(TaskSet):".format(klass=self.task_set_name),
            self.add_hooks(width),
            self.generate_on_start(width),
            self.generate_tasks(width)
        ]
        return join_str.join(behaviour_components)

    def locust_properties(self, width):
        properties = {
            "task_set": self.task_set_name,
            "min_wait": 5000,
            "max_wait": 9000
        }
        return "\n{w}".join(
            ["{key} = {value}".format(key=key, value=value) for key, value in properties.items()]
        ).format(**utils.StringDict(w=' ' * width * 4))

    def get_locust(self, width):
        return "class {klass}(HttpLocust):\n{w}{properties}".format(**utils.StringDict(
            klass=self.tag + "Locust",
            properties=self.locust_properties(width),
            w=' ' * 4
        ))

    def convert(self, width):
        return "{task_set}\n\n\n{locust}".format(**utils.StringDict(
            task_set=self.get_behaviour(width),
            locust=self.get_locust(width)
        ))
