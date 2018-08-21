from io import open
import os

import yaml

from settings.conf import settings
from scripts import (
    constants as swagger_constants,
    exceptions,
    utils
)


class AutoGenerator:
    """
    Auto Generate Resource Mapping from Swagger definition.
    Auto update Swagger definition
    """

    def __init__(self, swagger_file=None):

        self.swagger_file = swagger_file or settings.SWAGGER_FILE
        self.specs = self.read_specs()

        self.resources = self.read_resources()
        self.new_resources = set()

    @property
    def project_path(self):
        return os.path.join(settings.BASE_DIR, settings.PROJECT_FOLDER_NAME, settings.PROJECT_NAME)

    def read_resources(self):
        _file = os.path.join(self.project_path, settings.MAPPING_FILE)

        with open(_file) as mapping_file:
            ret_stream = yaml.safe_load(mapping_file)

        return ret_stream

    def add_resource(self, resource):
        if resource and resource not in self.resources:
            self.new_resources.add(resource)

    def read_specs(self):
        _file = os.path.join(self.project_path, self.swagger_file)

        with open(_file) as open_api_file:
            ret_stream = yaml.safe_load(open_api_file)

        return ret_stream

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

    def update_specs(self):
        _file = os.path.join(self.project_path, self.swagger_file)

        with open(_file, 'w') as open_api_file:
            yaml.dump(self.specs, open_api_file, default_flow_style=False)

    def update_resources(self):
        _file = os.path.join(self.project_path, settings.MAPPING_FILE)

        auto_resource = {resource: "# Add your definition here" for resource in self.new_resources}

        with open(_file, 'a+') as auto_write_file:
            yaml.dump(auto_resource, auto_write_file, default_flow_style=False)

    def update(self):
        self.update_specs()
        self.update_resources()


if __name__ == "__main__":
    gen = AutoGenerator()
    gen.parse()
    gen.update()
