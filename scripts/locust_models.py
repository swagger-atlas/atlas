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
        self.custom_url = False

        self.data_body = dict()
        self.query_params = dict()

        self.parse_parameters()

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
                w='\t' * width)
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
                resource = config.get(constants.RESOURCE)

                if resource:
                    self.decorators.append(self.create_resource_decorator(resource))
                    self.have_resource = True
                    self.custom_url = True
                else:
                    # if we do not have resource, we still need to make a valid URL
                    self.construct_query_parameter(config, param_type="path")

            elif in_ == constants.BODY_PARAM:
                schema = config.get(constants.SCHEMA)

                if not schema:
                    raise exceptions.ImproperSwaggerException("Body Parameter must specify schema")

                self.parse_schema(schema)

            elif in_ == constants.QUERY_PARAM:
                self.construct_query_parameter(config)

            elif in_ == constants.FORM_PARAM:
                form_data.append(config)

            else:
                raise exceptions.ImproperSwaggerException("Config {} does not have valid parameter type".format(config))

        if form_data:
            self.data_body[self.func_name] = form_data
            self.have_resource = True

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
        parameter_list = ["url"]
        if self.data_body:
            parameter_list.append("data=body(body_config)")
        if self.query_params:
            parameter_list.append("params=path_params")
        return ", ".join(parameter_list)

    def construct_body_variables(self):
        body_definition = []

        for key, value in self.data_body.items():
            body_definition.append("{key} = {config}".format(key="body_config", config=value))

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

        if query_str or path_str:
            # If one if present, we need to append both
            body_definition.append("query_config = {q}".format_map(utils.StringDict(q=query_str)))
            body_definition.append("path_config = {p}".format_map(utils.StringDict(p=path_str)))

            # Also get Path Parameters
            body_definition.append("url, path_params = formatted_url(url, query_config, path_config)")

        return body_definition

    def get_function_definition(self, width):

        body_definition = self.construct_body_variables()

        body_definition.append("self.client.{method}({params})".format_map(
            utils.StringDict(method=self.method, params=self.get_client_parameters())
        ))

        join_str = "\n{w}".format(w='\t'*width)
        return join_str.join(body_definition)

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

    def generate_tasks(self, width):
        join_string = "\n\n{w}".format(w='\t'*width)
        return join_string.join([_task.convert(width) for _task in self.tasks])

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
