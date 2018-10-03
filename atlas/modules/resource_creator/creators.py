import re

import inflection

from atlas.conf import settings
from atlas.modules import (
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
        self.spec_definitions = self.format_references(self.specs.get(swagger_constants.DEFINITIONS, {}).keys())

        self.resources = self.read_file_from_input(settings.MAPPING_FILE, {})
        self.resource_keys = self.format_references(self.resources.keys())
        self.new_resources = set()

        # Keep list of refs which are already processed to avoid duplicate processing
        self.processed_refs = set()

    @staticmethod
    def format_references(references) -> set:
        """
        Convert all resource keys to uniform format
        Uniformity is ensured by:
            - Making sure everything is in lower case
            - removing _, - from strings

        This does mean that abc_d, and ab_cd refers to same keys
        However, we estimate that this has lower probability
            than users writing Swagger correctly to adhere to correct casing in their references

        :return: Set of all Resource Keys
        """
        return {"".join([x.lower() for x in re.sub("-", "_", key).split("_")]) for key in references}

    def add_resource(self, resource):

        if not resource:
            return ""

        resource = "".join([x.lower() for x in re.sub("-", "_", resource).split("_")])

        if resource not in self.resource_keys:
            self.new_resources.add(resource)
            self.resource_keys.add(resource)

        return resource

    def add_reference_definition(self, reference, fields):
        """
        Add a virtual reference for every resource in Swagger definition
        """
        definitions = self.specs.get(swagger_constants.DEFINITIONS, {})

        if reference in self.spec_definitions or reference in self.processed_refs:
            return  # We already have reference with same name, or have processed it earlier, so do nothing

        definitions[reference] = {
            swagger_constants.TYPE: swagger_constants.OBJECT,
            # Without dict initialization, it is copying some auto-generated IDs also.
            # When have time, investigate!
            swagger_constants.PROPERTIES: {
                fields[swagger_constants.PARAMETER_NAME]: dict(fields)
            }
        }
        self.processed_refs.add(reference)

    @staticmethod
    def extract_resource_name_from_param(param_name, url_path):
        """
        Extract Resource Name from parameter name
        Names could be either snake case (foo_id) or camelCase (fooId)
        Return None if no such resource could be found
        """

        resource_name = None

        identifier_suffixes = {"_id", "Id", "_slug", "Slug", "pk"}

        for suffix in identifier_suffixes:
            if param_name.endswith(suffix):
                resource_name = param_name[:-len(suffix)]
                break

        # Resource Name not found by simple means.
        # Now, assume that resource could be available after the resource
        # For example: pets/{id} -- here most likely id refers to pet
        if not resource_name and param_name in {"id", "slug", "pk"}:
            url_array = url_path.split("/")
            resource_index = url_array.index(f'{{{param_name}}}') - 1
            if resource_index >= 0:
                # Singularize the resource
                resource_name = inflection.singularize(url_array[resource_index])

        return resource_name

    def parse_params(self, params, url):

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
                    resource = self.extract_resource_name_from_param(name, url)
                    if resource:
                        resource = self.add_resource(resource)
                        param[swagger_constants.RESOURCE] = resource
                        self.add_reference_definition(resource, param)

            elif param_type == swagger_constants.BODY_PARAM:
                self.resolve_body_param(param)

    def resolve_body_param(self, body_config):
        schema = body_config.get(swagger_constants.SCHEMA, {})
        self.resolve_schema(schema)

    def resolve_schema(self, schema):
        """
        We can only associate Complete references, and not in-line definitions
        """
        ref = schema.get(swagger_constants.REF)

        if ref:
            self.get_ref_name_and_config(ref)

    def get_ref_name_and_config(self, ref):
        ref_config = utils.resolve_reference(self.specs, ref)
        ref_name = ref.split("/")[-1]
        self.parse_reference(ref_name, ref_config)

    def parse_reference(self, ref_name, ref_config):

        if ref_name in self.processed_refs:
            return      # This has already been processed, so need to do it again

        for element in ref_config.get(swagger_constants.ALL_OF, []):
            self.resolve_schema(element)

        properties = ref_config.get(swagger_constants.PROPERTIES, {})

        for key, value in properties.items():
            if swagger_constants.REF in value:
                self.get_ref_name_and_config(value[swagger_constants.REF])
            elif key in ["id", "slug"]:
                resource = value.get(swagger_constants.RESOURCE, utils.convert_to_snake_case(ref_name))

                if resource:
                    resource = self.add_resource(resource)
                    value[swagger_constants.RESOURCE] = resource

        self.processed_refs.add(ref_name)

    def parse(self):

        for url, path_config in self.specs.get(swagger_constants.PATHS, {}).items():

            parameters = path_config.get(swagger_constants.PARAMETERS)

            if parameters:
                self.parse_params(parameters, url)

            for method, method_config in path_config.items():

                if method in swagger_constants.VALID_METHODS:
                    parameters = method_config.get(swagger_constants.PARAMETERS)

                    if parameters:
                        self.parse_params(parameters, url)

        for ref_name, ref_config in self.specs.get(swagger_constants.DEFINITIONS, {}).items():
            self.parse_reference(ref_name, ref_config)

    def update(self):

        # Update Specs File
        self.write_file_to_output(self.swagger_file, self.specs, append_mode=False)

        # Update Resource Mapping File
        auto_resource = {resource: {"def": "# Add your definition here"} for resource in self.new_resources}
        self.write_file_to_output(settings.MAPPING_FILE, {**self.resources, **auto_resource}, append_mode=False)
