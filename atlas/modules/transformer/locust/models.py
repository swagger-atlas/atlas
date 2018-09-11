import logging
import re

from atlas.modules import utils
from atlas.modules.transformer.base import models

logger = logging.getLogger(__name__)


class Task(models.Task):
    """
    Define a single Task of Locust File
    """

    def normalize_function_name(self):
        """
        Convert - into _
        """
        return re.sub("-", "_", self.open_api_op.func_name)

    def get_http_method_parameters(self):
        """
        Parameters for calling Request method
        """
        parameter_list = ["url"]
        if self.data_body:
            parameter_list.append("data=self.data_provider.generate_data(body_config)")
        if self.url_params:
            parameter_list.append("params=query_params")
        if self.headers:
            parameter_list.append("headers=self.data_provider.generate_data(header_config)")
        return ", ".join(parameter_list)

    def body_definition(self):
        body_definition = []

        if self.data_body:
            body_definition.append("body_config = {config}".format(config=self.data_body))

        if self.open_api_op.tags:
            body_definition.append("tags = [{}]".format(
                ", ".join(["'{}'".format(tag) for tag in self.open_api_op.tags])
            ))

        query_str, path_str = self.parse_url_params_for_body()
        url_str = "url = '{}'".format(self.open_api_op.url)
        body_definition.append(url_str)

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

        body_definition = self.body_definition()

        body_definition.append("self.client.{method}({params})".format_map(
            utils.StringDict(method=self.open_api_op.method, params=self.get_http_method_parameters())
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
