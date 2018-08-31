import random
import string

from modules.transformer import data_config


class Task:
    """
    A single task corresponds to single URL/Method combination function
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

        self.data_config = data_config.DataConfig(spec or {})

        self.data_body = dict()
        self.url_params = dict()

        self.headers = []

        self.parse_parameters()

    @staticmethod
    def normalize_function_name(func_name):
        raise NotImplementedError

    def parse_parameters(self):
        raise NotImplementedError

    def convert(self, width):
        raise NotImplementedError


class TaskSet:
    """
    Task Set is collection of tasks
    """

    def __init__(self, tasks, tag=None):
        self.tag = tag or ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.tasks = tasks

    def convert(self, width):
        raise NotImplementedError
