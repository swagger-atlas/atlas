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

    def generate(self, config):
        data_body = {}

        for item_name, item_config in config.items():

            # First, resolve references
            ref = item_config if item_name == constants.REF else item_config.get(constants.REF)
            if ref:
                ref_config = self.generate(
                    utils.resolve_reference(self.spec, ref).get(constants.PROPERTIES, {})
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