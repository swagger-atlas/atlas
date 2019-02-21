from atlas.modules import constants, utils


class SchemaResolver:
    """
    Resolves the Swagger Schema.
    This involves recursively resolving sub-schemas, objects and arrays till we reach element/field configuration

    Sample Usage of class:
        data_schema_resolver = SchemaResolver(swagger_specs)
        data_schema = data_schema_resolver.resolve(data_schema)
    """

    def __init__(self, spec):
        self.spec = spec

        # Maintain a list of resolved refs, to avoid cycles
        self.visited_ref = set()

        # If you want to use the property, call resolve_with_read_only_fields as your entry function instead of resolve
        # By default, when resolving schema, we ignore read-only fields, and they are not returned in resolved schema
        self.include_read_only = False

        # Ideally, this should not be implemented as instance variable
        # Correct fix would be to implement Schema class, and make this instance variable of that class
        # Doing that would involve much refactoring though
        self.is_top_level = True

    def resolve_element_config(self, item_config: dict):
        item_data = {}
        for key, value in item_config.items():
            if isinstance(value, dict):
                item_data.update(self.resolve({key: value}, is_field=True))
            elif key in constants.EXTRA_KEYS:
                # This should be else of previous Condition
                # Since nested references can use this as property
                continue
            else:
                item_data[key] = value
        return item_data

    def resolve_with_read_only_fields(self, *args, **kwargs):
        """
        Entry function for the class if you want to also include read-only fields in your final resolved schema
        """
        self.include_read_only = True
        ret = self.resolve(*args, **kwargs)
        self.include_read_only = False
        return ret

    def process_additional_properties(self, config):
        """
        This process Additional properties for Schema object.
        Additional properties are free-form dict fields
        Here we make sure that they are added, and it would be upto provider to generate data as fit for them
        """

        data_body = {}

        additional_properties = config.get(constants.ADDITIONAL_PROPERTIES, {})

        if additional_properties:
            ref = additional_properties.get(constants.REF)
            data_body[constants.ADDITIONAL_PROPERTIES] = (
                self.resolve(utils.resolve_reference(self.spec, ref))
                if ref else self.resolve_element_config(additional_properties)
            )
            data_body[constants.MIN_PROPERTIES] = config.get(constants.MIN_PROPERTIES, 0)

        return data_body

    def top_level_changes(self, config, data_body):
        if self.is_top_level:
            data_body[constants.TYPE] = config.get(constants.TYPE, constants.OBJECT)
            self.is_top_level = False
        return data_body

    def resolve(self, config, is_field=False):
        """
        Generates the schema for Load testing file
        Runs as following:
            1. First check for ALL OF. If yes, recursively parse each sub-schema
            2. Then, check for Additional Properties, and add free fields
            3. Go through Properties, and make sure that references are parsed correctly as needed

        Resolve is recursive method at several depths (i.e. it may call func which may call generate and so on),
        Do do not manipulate instance variables unless you know what you are doing.
        """

        data_body = {}

        if not config:
            return data_body

        # ALL_OF and Additional properties may be names of data fields
        # We want to only process these attributes when they are top-attribute of references
        if not is_field:
            all_of_config = config.get(constants.ALL_OF, [])

            for element in all_of_config:
                data_body.update(self.resolve(element))

            if all_of_config:
                return data_body

            data_body = self.process_additional_properties(config)

        properties = config.get(constants.PROPERTIES)   # Do not add default blank dict here, since it is checked
        if properties or properties == {}:      # Properties could be blank dict, which is perfectly fine
            config = properties

        data_body = self.top_level_changes(config, data_body)
        data_body = self.parse_properties(config, data_body)
        return data_body

    def parse_properties(self, config, data_body):

        for item_name, item_config in config.items():
            if item_name == constants.REF:
                ref = item_config
            else:
                # First check whether Item config is a dict.
                if isinstance(item_config, dict):
                    ref = item_config.get(constants.REF)
                else:
                    continue    # This is A reference where we cannot do anything

            # We only parse string references
            if ref and not isinstance(ref, str):
                continue

            if ref and ref not in self.visited_ref:
                self.visited_ref.add(ref)
                ref_config = self.resolve(
                    utils.resolve_reference(self.spec, ref)
                )
                if item_name == constants.REF:
                    data_body = ref_config  # This is top-level reference, so replace complete body
                else:
                    # This is field-level reference
                    data_body[item_name] = {constants.TYPE: constants.OBJECT, constants.PROPERTIES: ref_config}
                self.visited_ref.remove(ref)
                continue  # We generated the data already, move on to next once

            # Do not generate data for Read-only fields unless explicitly over-written
            read_only = item_config.get(constants.READ_ONLY, False)
            if read_only and not self.include_read_only:
                continue

            # If it is resource, we only need resource mapping
            resource = item_config.get(constants.RESOURCE)
            data_body[item_name] = (
                {constants.RESOURCE: resource} if resource else self.resolve_element_config(item_config)
            )

        return data_body
