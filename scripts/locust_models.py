import logging
import random
import string

from scripts import (
    constants,
    exceptions,
    utils
)

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

        self.func_name = func_name
        self.method = method
        self.url = url
        self.parameters = parameters or {}

        self.spec = spec or {}

        self.decorators = ["@task(1)"]
        self.have_resource = False

        self.data_body = dict()

        self.parse_parameters()

    @staticmethod
    def get_function_parameters():
        parameter_list = ["self", "format_url", "**kwargs"]
        return ", ".join(parameter_list)

    def get_function_declaration(self, width):
        return "{decorators}\n{w}def {name}({parameters}):".format(
            **utils.StringDict(
                decorators=self.get_decorators(width), name=self.func_name, parameters=self.get_function_parameters(),
                w='\t' * width)
        )

    def parse_parameters(self):
        """
        For the Path parameters, add required resources
        For the body parameter, add the definition
        """
        for config in self.parameters.values():
            in_ = config.get(constants.IN_)

            if not in_:
                raise exceptions.ImproperSwaggerException("In is required field for OpenAPI Parameter")

            if in_ == constants.PATH_PARAM:
                resource = config.get(constants.RESOURCE)

                if resource:
                    self.decorators.append(self.create_resource_decorator(resource))
                    self.have_resource = True

            if in_ == constants.BODY_PARAM:
                schema = config.get(constants.SCHEMA)

                if not schema:
                    raise exceptions.ImproperSwaggerException("Body Parameter must specify schema")

                self.parse_schema(schema)

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
        self.have_resource = True

    def create_resource_decorator(self, resource):
        return "@{res_method}(resource={resource}, url={url})".format(**utils.StringDict(
            res_method=constants.RESOURCE_MAPPING.get(self.method),
            resource=resource, url=self.url
        ))

    def get_client_parameters(self):
        """
        Parameters for calling Request method
        """
        parameter_list = ["format_url"]
        if self.data_body:
            parameter_list.append("data=body({})".format(self.func_name + "_CONFIG"))
        return ", ".join(parameter_list)

    def get_function_definition(self, width):
        return "self.client.{method}({params})".format(**utils.StringDict(
            method=self.method, params=self.get_client_parameters()
        ))

    def get_decorators(self, width):
        return "\n{w}".join(self.decorators).format_map(utils.StringDict(w='\t' * width))

    def convert(self, width):
        """
        Convert the task to function
        """

        components = ["{declaration}", "{definition}"]
        return "\n{w}".join(components).format(**utils.StringDict(
            declaration=self.get_function_declaration(width - 1), definition=self.get_function_definition(width),
            w='\t' * width
        ))


class TaskSet:

    def __init__(self, tasks, tag=None):
        self.tag = tag or ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        self.tasks = tasks

    @property
    def have_resource(self):
        return any([task.have_resource for task in self.tasks])

    @property
    def body_declarations(self):
        return [
            "{key} = {config}".format(key=key+"_CONFIG", config=value)
            for task in self.tasks
            for key, value in task.data_body.items()
        ]

    def generate_tasks(self, width):
        return "\n\n{w}".join([_task.convert(width) for _task in self.tasks]).format_map(
            utils.StringDict(w='\t' * width))

    @staticmethod
    def generate_on_start():
        return ""

    @property
    def task_set_name(self):
        return self.tag + "Behaviour"

    def get_behaviour(self, width):
        return "class {klass}(TaskSet):\n\t{on_start}\n\t{tasks}".format(**utils.StringDict(
            klass=self.task_set_name,
            on_start=self.generate_on_start(),
            tasks=self.generate_tasks(width + 1)
        ))

    def locust_properties(self, width):
        properties = {
            "task_set": self.task_set_name,
            "min_wait": 5000,
            "max_wait": 9000
        }
        return "\n{w}".join(
            ["{key} = {value}".format(key=key, value=value) for key, value in properties.items()]
        ).format(**utils.StringDict(w='\t' * width))

    def get_locust(self, width):
        return "class {klass}(HttpLocust):\n\t{properties}".format(**utils.StringDict(
            klass=self.tag + "Locust",
            properties=self.locust_properties(width)
        ))

    def convert(self, width):
        return "{task_set}\n\n{locust}".format(**utils.StringDict(
            task_set=self.get_behaviour(width),
            locust=self.get_locust(width)
        ))
