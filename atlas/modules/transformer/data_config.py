from atlas.modules import constants, utils


class DataConfig:

    def __init__(self, spec):
        self.spec = spec

    def resolve_item_config(self, item_config):
        item_data = {}
        for key, value in item_config.items():
            if isinstance(value, dict):
                item_data.update(self.generate({key: value}))
            elif key in constants.EXTRA_KEYS:
                # This should be else of previous Condition
                # Since nested references can use this as property
                continue
            else:
                item_data[key] = value
        return item_data

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
                self.generate(utils.resolve_reference(self.spec, ref))
                if ref else self.resolve_item_config(additional_properties)
            )
            data_body[constants.MIN_PROPERTIES] = config.get(constants.MIN_PROPERTIES, 0)

        return data_body

    def generate(self, config):
        """
        Generates the schema for Load testing file
        Runs as following:
            1. First check for ALL OF. If yes, recursively parse each sub-schema
            2. Then, check for Additional Properties, and add free fields
            3. Go through Properties, and make sure that references are parsed correctly as needed
        """

        data_body = {}
        all_of_config = config.get(constants.ALL_OF, [])

        for element in all_of_config:
            data_body.update(self.generate(element))

        if all_of_config:
            return data_body

        data_body = self.process_additional_properties(config)

        properties = config.get(constants.PROPERTIES, {})
        if properties:
            config = properties

        for item_name, item_config in config.items():

            # First, resolve references
            ref = item_config if item_name == constants.REF else item_config.get(constants.REF)
            if ref:
                ref_config = self.generate(
                    utils.resolve_reference(self.spec, ref)
                )
                if item_name == constants.REF:
                    data_body = ref_config  # This is top-level reference, so replace complete body
                else:
                    # This is field-level reference
                    data_body[item_name] = {constants.TYPE: constants.OBJECT, constants.PROPERTIES: ref_config}
                continue  # We generated the data already, move on to next once

            # Do not generate data for Read-only fields
            read_only = item_config.get(constants.READ_ONLY, False)
            if read_only:
                continue

            # If it is resource, we only need resource mapping
            resource = item_config.get(constants.RESOURCE)
            data_body[item_name] = {constants.RESOURCE: resource} if resource else self.resolve_item_config(item_config)

        return data_body
