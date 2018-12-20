import re

from atlas.conf import settings
from atlas.modules import (
    constants as swagger_constants,
    exceptions,
    mixins,
    utils
)
from atlas.modules.helpers import resource_map


class AutoGenerator(mixins.YAMLReadWriteMixin):
    """
    Auto Generate Resource Mapping from Swagger definition.
    Auto update Swagger definition
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

        for param in params:

            ref = param.get(swagger_constants.REF)
            if ref:
                param = utils.resolve_reference(self.specs, ref)

            param_type = param.get(swagger_constants.IN_)

            if not param_type:
                raise exceptions.ImproperSwaggerException("Param type not defined for {}".format(param))

            if param_type in swagger_constants.URL_PARAMS:

                name = param.get(swagger_constants.PARAMETER_NAME)

                if not name:
                    raise exceptions.ImproperSwaggerException("Param name not defined for {}".format(param))

                # Check if resource is defined
                resource = param.get(swagger_constants.RESOURCE)

                # Generate resources if none found. Do not generate if empty string
                if resource is None:
                    resource = self.extract_resource_name_from_param(name, url, param_type)

                if resource:
                    resource = self.add_resource(resource)
                    resource_alias = self.resource_map_resolver.get_alias(resource)
                    param[swagger_constants.RESOURCE] = resource_alias
                    self.add_reference_definition(resource_alias, param)

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

    def resolve_all_of_element(self, ref_name, schema):

        # Try resolving any references
        self.resolve_schema(schema)

        _type = schema.get(swagger_constants.TYPE)
        if _type == swagger_constants.OBJECT:
            self.parse_reference_properties(ref_name, schema.get(swagger_constants.PROPERTIES))

    def get_ref_name_and_config(self, ref):
        ref_config = utils.resolve_reference(self.specs, ref)
        ref_name = ref.split("/")[-1]
        self.parse_reference(ref_name, ref_config)

    def parse_reference(self, ref_name, ref_config):

        if ref_name in self.processed_refs:
            return      # This has already been processed, so need to do it again

        for element in ref_config.get(swagger_constants.ALL_OF, []):
            self.resolve_all_of_element(ref_name, element)

        self.parse_reference_properties(ref_name, ref_config.get(swagger_constants.PROPERTIES, {}))

    def parse_reference_properties(self, ref_name, properties):

        for key, value in properties.items():
            resource = ""
            if key in settings.SWAGGER_REFERENCE_FIELD_RESOURCE_IDENTIFIERS:
                resource = value.get(swagger_constants.RESOURCE, utils.convert_to_snake_case(ref_name))
                value[swagger_constants.READ_ONLY] = True
            elif swagger_constants.REF in value:
                self.get_ref_name_and_config(value[swagger_constants.REF])

            # elif key in self.resource_keys:
            #     resource = key

            if resource:
                resource = self.add_resource(resource)
                resource_alias = self.resource_map_resolver.get_alias(resource)
                value[swagger_constants.RESOURCE] = resource_alias

        self.processed_refs.add(ref_name)

    def parse(self):

        for url, path_config in self.specs.get(swagger_constants.PATHS, {}).items():

            parameters = path_config.get(swagger_constants.PARAMETERS)

            if parameters:
                self.parse_params(parameters, url)

            for method, method_config in path_config.items():

                if method in swagger_constants.VALID_METHODS:
                    parameters = method_config.get(swagger_constants.PARAMETERS)

                    # Detect Operation ID in swagger, and if not present, generate and write back in Swagger
                    # Operation IDs are used as primary key throughout application
                    op_id = method_config.get(swagger_constants.OPERATION)
                    if not op_id:
                        method_config[swagger_constants.OPERATION] = self.operation_id_name(url, method)

                    if parameters:
                        self.parse_params(parameters, url)

        for ref_name, ref_config in self.specs.get(swagger_constants.DEFINITIONS, {}).items():
            self.parse_reference(ref_name, ref_config)

    @staticmethod
    def operation_id_name(url, method) -> str:
        """
        Generate the name for Operation ID

        Logic:
            user/       - (user_create, user_list)
            user/{id}   - (user_read, user_update, user_delete)
            user/{id}/action - (user_action with above logic)
        """

        url_fragments = [fragment for fragment in url.split("/") if fragment]

        op_name_array = [
            url_element for url_element in url_fragments if not url_element.startswith("{")
        ]

        if method == swagger_constants.DELETE:
            op_name_array.append("delete")
        elif url_fragments[-1].startswith("{"):
            op_name_array.append("read" if method == swagger_constants.GET else "update")
        else:
            op_name_array.append("list" if method == swagger_constants.GET else "create")

        return "_".join(op_name_array)

    def update(self):

        # Update Specs File
        self.write_file_to_output(self.swagger_file, self.specs, append_mode=False)

        # Update Resource Mapping File
        auto_resource = {resource: {"def": "# Add your definition here"} for resource in self.new_resources}
        self.write_file_to_input(
            settings.MAPPING_FILE, {**self.resource_map_resolver.resource_map, **auto_resource}, append_mode=False
        )
