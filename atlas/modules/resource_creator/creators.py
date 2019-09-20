import re

from atlas.conf import settings
from atlas.modules import (
    constants as swagger_constants,
    exceptions,
    mixins,
    utils
)
from atlas.modules.resource_data_generator import constants as resource_constants
from atlas.modules.helpers import resource_map


class AutoGenerator(mixins.YAMLReadWriteMixin):
    """
    Auto Generate Resource Mapping from Swagger definition.
    Auto update Swagger definition and Resource Mapping file
    """

    def __init__(self, swagger_file=None):
        super().__init__()

        self.swagger_file = swagger_file or settings.SWAGGER_FILE
        self.specs = self.read_file_from_input(self.swagger_file, {})
        self.spec_definitions = self.format_references(self.specs.get(swagger_constants.DEFINITIONS, {}).keys())

        self.resource_map_resolver = resource_map.ResourceMapResolver()
        self.resource_map_resolver.resolve_resources()

        self.resource_keys = self.format_references(self.resource_map_resolver.resource_map.keys())
        self.new_resources = set()

        # Keep list of refs which are already processed to avoid duplicate processing
        self.processed_refs = set()

        # For any single operation, maintain a list of parameters
        self.resource_params = set()

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

    def extract_resource_name_from_param(self, param_name, url_path, param_type=swagger_constants.PATH_PARAM):
        """
        Extract Resource Name from parameter name
        Names could be either snake case (foo_id) or camelCase (fooId)
        In case of URL Params, further they could be foo/id
        Return None if no such resource could be found
        """

        resource_name = utils.extract_resource_name_from_param(param_name, url_path, param_type)

        if not resource_name and param_name in self.resource_keys:
            resource_name = param_name

        return resource_name

    def parse_params(self, params, url):

        # Reset the params
        self.resource_params = set()

        for param in params:

            ref = param.get(swagger_constants.REF)
            if ref:
                param = utils.resolve_reference(self.specs, ref)

            param_type = param.get(swagger_constants.IN_)
            _name = param.get(swagger_constants.PARAMETER_NAME)

            if not param_type:
                raise exceptions.ImproperSwaggerException(f"Param type not defined for {_name}")

            if param_type in swagger_constants.URL_PARAMS:

                # Check if resource is defined
                resource = param.get(swagger_constants.RESOURCE)

                # Generate resources if none found. Do not generate if empty string
                if resource is None:
                    resource = self.extract_resource_name_from_param(_name, url, param_type)

                if resource:
                    resource = self.add_resource(resource)
                    resource_alias = self.resource_map_resolver.get_alias(resource)
                    param[swagger_constants.RESOURCE] = resource_alias
                    self.add_reference_definition(resource_alias, param)
                    self.resource_params.add(resource_alias)

            elif param_type == swagger_constants.BODY_PARAM:
                self.resolve_body_param(param)

        return self.resource_params

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

    def resolve_all_of_element(self, ref_name, schema):

        # Try resolving any references
        self.resolve_schema(schema)

        _type = schema.get(swagger_constants.TYPE)
        if _type == swagger_constants.OBJECT:
            self.parse_reference_properties(ref_name, schema.get(swagger_constants.PROPERTIES, {}))

    def get_ref_name_and_config(self, ref):

        if not isinstance(ref, str):
            print(f"\nWARNING: Only string references supported. Found: {ref}\n")
            return

        ref_config = utils.resolve_reference(self.specs, ref)
        ref_name = ref.split("/")[-1]
        self.parse_reference(ref_name, ref_config)

    def parse_reference(self, ref_name, ref_config):

        if ref_name in self.processed_refs:
            return      # This has already been processed, so no need to do it again

        for element in ref_config.get(swagger_constants.ALL_OF, []):
            self.resolve_all_of_element(ref_name, element)

        self.parse_reference_properties(ref_name, ref_config.get(swagger_constants.PROPERTIES, {}))

    def parse_reference_properties(self, ref_name, properties):

        # By adding it to processed list before even processing, we avoid cycles
        self.processed_refs.add(ref_name)

        for key, value in properties.items():
            resource = ""
            if key in settings.SWAGGER_REFERENCE_FIELD_RESOURCE_IDENTIFIERS:
                resource = value.get(swagger_constants.RESOURCE, utils.convert_to_snake_case(ref_name))
                value[swagger_constants.READ_ONLY] = True
            elif swagger_constants.REF in value:
                self.get_ref_name_and_config(value[swagger_constants.REF])

            # Commenting this out, as adding this logic generated lots of false positive resources
            # elif key in self.resource_keys:
            #     resource = key

            if resource:
                resource = self.add_resource(resource)
                resource_alias = self.resource_map_resolver.get_alias(resource)
                value[swagger_constants.RESOURCE] = resource_alias
                self.resource_params.add(resource_alias)

    def parse(self):

        for url, path_config in self.specs.get(swagger_constants.PATHS, {}).items():

            parameters = path_config.get(swagger_constants.PARAMETERS)
            common_resources = set()

            if parameters:
                common_resources = self.parse_params(parameters, url)

            for method, method_config in path_config.items():

                method_resources = set()

                if method in swagger_constants.VALID_METHODS:
                    parameters = method_config.get(swagger_constants.PARAMETERS)

                    # Detect Operation ID in swagger, and if not present, generate and write back in Swagger
                    # Operation IDs are used as primary key throughout application
                    op_id = method_config.get(swagger_constants.OPERATION)
                    if not op_id:
                        method_config[swagger_constants.OPERATION] = utils.operation_id_name(url, method)

                    if parameters:
                        method_resources = self.parse_params(parameters, url)

                    all_resources = common_resources.union(method_resources)

                    if len(all_resources) > 1:
                        method_config[swagger_constants.DEPENDENT_RESOURCES] = all_resources

        for ref_name, ref_config in self.specs.get(swagger_constants.DEFINITIONS, {}).items():
            self.parse_reference(ref_name, ref_config)

    def update(self):

        # Update Specs File
        self.write_file_to_output(self.swagger_file, self.specs, append_mode=False)

        # Update Resource Mapping File
        auto_resource = {
            resource: {resource_constants.DUMMY_DEF: "# Add your definition here"} for resource in self.new_resources
        }
        self.write_file_to_input(
            settings.MAPPING_FILE, {**self.resource_map_resolver.resource_map, **auto_resource}, append_mode=False
        )
