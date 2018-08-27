import logging
from collections import OrderedDict

from scripts import (
    constants as swagger_constants,
    exceptions,
    locust_models
)
from settings.conf import settings

logger = logging.getLogger(__name__)


class Operation:
    """
    Define an OpenAPI Specific Operation
    """

    def __init__(self, url, method, config, spec=None):

        self.url = url
        self.method = method
        self.config = config

        # Complete Swagger Spec Model
        self.spec = spec or {}

        self.parameters = OrderedDict()

    def validate_method(self):
        if self.method not in swagger_constants.VALID_METHODS:
            raise exceptions.ImproperSwaggerException("Invalid Method {} for {}".format(self.method, self.url))

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

    def get_task(self):

        func_name = self.config.get(swagger_constants.OPERATION)
        self.add_parameters(self.config.get(swagger_constants.PARAMETERS, []))

        return locust_models.Task(func_name=func_name, parameters=self.parameters, url=self.url, method=self.method,
                                  spec=self.spec)


class OpenAPISpec:

    def __init__(self, spec):
        self.spec = spec

        self.paths = OrderedDict()
        self.tasks = []

    def get_tasks(self):

        paths = self.spec.get(swagger_constants.PATHS, {})

        for path, config in paths.items():

            # We do not include Logout URL in our Load Test
            if path == settings.LOGOUT_API_URL:
                continue

            common_parameters = config.pop(swagger_constants.PARAMETERS, [])

            for method, method_config in config.items():

                if method in swagger_constants.VALID_METHODS:
                    operation = Operation(url=path, method=method, config=method_config, spec=self.spec)
                    operation.add_parameters(common_parameters)
                    self.tasks.append(operation.get_task())
                else:
                    logger.warning("Incorrect method - %s %s", method, method_config)
