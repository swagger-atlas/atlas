import logging
import re

from modules import (
    constants,
    exceptions,
    utils
)
from modules.transformer.base import models
from settings.conf import settings

logger = logging.getLogger(__name__)


class Task(models.Task):
    """
    Define a single Task of Locust File
    """

    @staticmethod
    def normalize_function_name(func_name):
        """
        Convert - into _
        """

        return re.sub("-", "_", func_name)

    def parse_parameters(self):
        """
        For the Path parameters, add required resources
        For the body parameter, add the definition
        """

        for config in self.parameters.values():
            in_ = config.get(constants.IN_)

            if not in_:
                raise exceptions.ImproperSwaggerException("In is required field for OpenAPI Parameter")

            name = config.get(constants.PARAMETER_NAME)

            if not name:
                raise exceptions.ImproperSwaggerException("Config {} does not have name".format(config))

            if in_ == constants.PATH_PARAM:
                self.construct_url_parameter(name, config, param_type="path")

            elif in_ == constants.BODY_PARAM:
                schema = config.get(constants.SCHEMA)
                if not schema:
                    raise exceptions.ImproperSwaggerException("Body Parameter must specify schema")
                self.data_body = schema

            elif in_ == constants.QUERY_PARAM:
                self.construct_url_parameter(name, config)

            elif in_ == constants.FORM_PARAM:
                self.data_body[name] = config

            elif in_ == constants.HEADER_PARAM:
                self.parse_header_params(name, config)

            else:
                raise exceptions.ImproperSwaggerException("Config {} does not have valid parameter type".format(config))

        self.data_body = self.data_config.generate(self.data_body)

    def parse_header_params(self, name, config):
        config = self.data_config.generate({name: config})
        if config:
            self.headers.append("'{name}': {config}".format(name=name, config=config[name]))

    def construct_url_parameter(self, name, config, param_type="query"):
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

    def get_client_parameters(self):
        """
        Parameters for calling Request method
        """
        parameter_list = ["url"]
        if self.data_body:
            parameter_list.append("data=self.data_provider.generate_data(body_config)")
        if self.url_params:
            parameter_list.append("params=path_params")
        if self.headers:
            parameter_list.append("headers=self.data_provider.generate_data(header_config)")
        return ", ".join(parameter_list)

    def construct_body_variables(self):
        body_definition = []

        if self.data_body:
            body_definition.append("body_config = {config}".format(config=self.data_body))

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
        url_str = "url = '{}'".format(self.url)

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
            body_definition.append(
                "url, path_params = self.format_url(url, query_config, path_config)"
            )

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

    def convert(self, width):
        """
        Convert the task to function
        """

        components = [
            "@task(1)\n{w}def {name}(self):".format(**utils.StringDict(name=self.func_name, w=' ' * (width-1) * 4)),
            "{definition}"
        ]
        return "\n{w}".join(components).format(**utils.StringDict(
            definition=self.get_function_definition(width), w=' ' * width * 4
        ))


class TaskSet(models.TaskSet):

    def generate_tasks(self, width):
        join_string = "\n\n{w}".format(w=' ' * width * 4)
        return join_string.join([_task.convert(width + 1) for _task in self.tasks])

    @staticmethod
    def generate_on_start(width):
        statements = [
            "def on_start(self):",
            "hook = LocustHook()",
            "self.profile, self.auth = hook.login(self.client)"
        ]
        join_str = "\n{w}".format(w=' ' * (width + 1) * 4)
        return join_str.join(statements)

    @staticmethod
    def data_provider(width):
        statements = [
            "@property\n{w}def data_provider(self):".format(w=' ' * width * 4),
            "return Provider(profile=self.profile)"
        ]
        join_string = "\n{w}".format(w=' ' * (width + 1) * 4)
        return join_string.join(statements)

    @staticmethod
    def format_url(width):
        statements = [
            "def format_url(self, url, query_config, path_config):",
            "path_params = self.data_provider.generate_data(path_config)",
            "url = url.format(**path_params)",
            "query_params = self.data_provider.generate_data(query_config)",
            "return url, query_params"
        ]
        join_string = "\n{w}".format(w=' ' * (width + 1) * 4)
        return join_string.join(statements)

    @property
    def task_set_name(self):
        return self.tag + "Behaviour"

    @staticmethod
    def add_class_vars(width):
        class_vars = [
            "profile = ''",
            "auth = ''"
        ]
        return "\n{w}".format(w=' ' * width * 4).join(class_vars)

    def get_behaviour(self, width):
        join_str = "\n\n{w}".format(w=' ' * width * 4)
        behaviour_components = [
            "class {klass}(TaskSet):".format(klass=self.task_set_name),
            self.add_class_vars(width),
            self.generate_on_start(width),
            self.data_provider(width),
            self.format_url(width),
            self.generate_tasks(width)
        ]
        return join_str.join(behaviour_components)

    def locust_properties(self, width):
        properties = {
            "task_set": self.task_set_name,
            "min_wait": 1000,
            "max_wait": 3000
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
