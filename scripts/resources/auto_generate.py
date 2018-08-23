from settings.conf import settings
from scripts import (
    constants as swagger_constants,
    exceptions,
    utils
)


class AutoGenerator(utils.YAMLReadWriteMixin):
    """
    Auto Generate Resource Mapping from Swagger definition.
    Auto update Swagger definition
    """

    def __init__(self, swagger_file=None):

        self.swagger_file = swagger_file or settings.SWAGGER_FILE
        self.specs = self.read_file(self.swagger_file, {})

        self.resources = self.read_file(settings.MAPPING_FILE, {})
        self.new_resources = set()

    def add_resource(self, resource):
        if resource and resource not in self.resources:
            self.new_resources.add(resource)

    def parse_params(self, params):

        for param in params:
            param_type = param.get(swagger_constants.IN_)

            if not param_type:
                raise exceptions.ImproperSwaggerException("Param type not defined for {}".format(param))

            if param_type == swagger_constants.PATH_PARAM:

                name = param.get(swagger_constants.PARAMETER_NAME)

                if not name:
                    raise exceptions.ImproperSwaggerException("Param name not defined for {}".format(param))

                # Check if resource is defined
                resource = param.get(swagger_constants.RESOURCE)

                if resource is not None:    # Empty strings should be respected
                    self.add_resource(resource)

                elif name.endswith("_id"):
                    resource = name[:-len("_id")]
                    param[swagger_constants.RESOURCE] = resource
                    self.add_resource(resource)

    def parse_reference(self, ref_name, ref_config):

        properties = ref_config.get(swagger_constants.PROPERTIES)

        if properties is None:      # Properties can be empty dictionary, which is fine
            raise exceptions.ImproperSwaggerException("Properties must be defined for {}".format(ref_name))

        ref_id = properties.get("id")

        if ref_id:
            resource = ref_id.get(swagger_constants.RESOURCE, utils.convert_to_snake_case(ref_name))

            if resource:
                ref_config[swagger_constants.RESOURCE] = resource
                self.add_resource(resource)

    def parse(self):
        paths = self.specs.get(swagger_constants.PATHS, {})
        self.parse_paths(paths)

        references = self.specs.get(swagger_constants.DEFINITIONS)
        for ref_name, ref_config in references.items():
            self.parse_reference(ref_name, ref_config)

    def parse_paths(self, paths):

        for path in paths.values():

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
        self.write_file(self.swagger_file, self.specs)

        # Update Resource Mapping File
        auto_resource = {resource: "# Add your definition here" for resource in self.new_resources}
        self.write_file(settings.MAPPING_FILE, auto_resource)


if __name__ == "__main__":
    gen = AutoGenerator()
    gen.parse()
    gen.update()
