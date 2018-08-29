from settings.conf import settings
from scripts import (
    constants as swagger_constants,
    exceptions,
    mixins,
    utils
)


class AutoGenerator(mixins.YAMLReadWriteMixin):
    """
    Auto Generate Resource Mapping from Swagger definition.
    Auto update Swagger definition
    """

    def __init__(self, swagger_file=None):

        self.swagger_file = swagger_file or settings.SWAGGER_FILE
        self.specs = self.read_file_from_input(self.swagger_file, {})

        self.resources = self.read_file_from_input(settings.MAPPING_FILE, {})
        self.new_resources = set()

    def add_resource(self, resource):
        if resource and resource not in self.resources:
            self.new_resources.add(resource)

    @staticmethod
    def extract_resource_name_from_param(param_name):
        """
        Extract Resource Name from parameter name
        Names could be either snake case (foo_id) or camelCase (fooId)
        Return None if no such resource could be found
        """

        resource_name = None

        if param_name.endswith("_id"):
            resource_name = param_name[:-len("_id")]

        elif param_name.endswith("Id"):
            resource_name = param_name[:-len("Id")]

        return resource_name

    def parse_params(self, params):

        for param in params:
            param_type = param.get(swagger_constants.IN_)

            if not param_type:
                raise exceptions.ImproperSwaggerException("Param type not defined for {}".format(param))

            if param_type in swagger_constants.URL_PARAMS:

                name = param.get(swagger_constants.PARAMETER_NAME)

                if not name:
                    raise exceptions.ImproperSwaggerException("Param name not defined for {}".format(param))

                # Check if resource is defined
                resource = param.get(swagger_constants.RESOURCE)

                if resource is not None:    # Empty strings should be respected
                    self.add_resource(resource)
                elif not resource:          # If resource is explicitly empty string, we should not generate them
                    resource = self.extract_resource_name_from_param(name)
                    if resource:
                        param[swagger_constants.RESOURCE] = resource
                        self.add_resource(resource)

            elif param_type == swagger_constants.BODY_PARAM:
                self.resolve_body_param(param)

    def resolve_body_param(self, param_config):
        schema = param_config.get(swagger_constants.SCHEMA, {})

        ref = schema.get(swagger_constants.REF)

        if ref:
            ref_config = utils.resolve_reference(self.specs, ref)
            ref_name = ref.split("/")[-1]
            self.parse_reference(ref_name, ref_config)
        # We have no way to map in-line obj def. to a resource

    def parse_reference(self, ref_name, ref_config):

        properties = ref_config.get(swagger_constants.PROPERTIES)

        if properties is None:      # Properties can be empty dictionary, which is fine
            raise exceptions.ImproperSwaggerException("Properties must be defined for {}".format(ref_name))

        ref_id = properties.get("id", {})

        if ref_id:
            resource = ref_id.get(swagger_constants.RESOURCE, utils.convert_to_snake_case(ref_name))

            if resource:
                ref_id[swagger_constants.RESOURCE] = resource
                self.add_resource(resource)

    def parse(self):

        for path in self.specs.get(swagger_constants.PATHS, {}).values():

            parameters = path.get(swagger_constants.PARAMETERS)

            if parameters:
                self.parse_params(parameters)

            for method, method_config in path.items():

                if method in swagger_constants.VALID_METHODS:
                    parameters = method_config.get(swagger_constants.PARAMETERS)

                    if parameters:
                        self.parse_params(parameters)

    def update(self):

        # Update Specs File
        self.write_file_to_output(self.swagger_file, self.specs, append_mode=False)

        # Update Resource Mapping File
        auto_resource = {resource: "# Add your definition here" for resource in self.new_resources}
        self.write_file_to_output(settings.MAPPING_FILE, {**self.resources, **auto_resource}, append_mode=False)


if __name__ == "__main__":
    gen = AutoGenerator()
    gen.parse()
    gen.update()
