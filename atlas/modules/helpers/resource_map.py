from atlas.modules import mixins
from atlas.modules.resource_data_generator import constants as resource_constants
from atlas.conf import settings


class ResourceMapResolver(mixins.YAMLReadWriteMixin):
    """
    Resolves Resource Map, and returns resolved configs
    """

    def __init__(self):
        super().__init__()
        self.resource_map = self.read_file_from_input(settings.MAPPING_FILE) or {}
        self.resource_config = {}

        # One of the major concept in Resource mapping relates to Aliases
        # Different entries in resource map may mean exactly same thing
        # We use alias map to track such entries
        self.alias_map = {}

        # Globals are actions which are applied to all resources in resource mapping
        # We need to extract them separately and apply the required actions to each resource as required
        self.globals = {}

    def get_config(self, resource):
        return self.resource_config.get(resource, self.resource_map.get(resource))

    def set_config(self, resource, config):
        self.resource_config[resource] = config

    def set_alias(self, resource, alias):
        self.alias_map[resource] = alias

    def get_alias(self, resource):
        return self.alias_map.get(resource, resource)

    def resolve(self, resource):
        """
        Recursive function to resolve single resource
        """
        config = self.get_config(resource)

        parent_resource = config.get(resource_constants.RESOURCE, None)

        if parent_resource:
            parent_config = self.resolve(parent_resource)

            # if config is empty, i.e. it does not contain anything except reference to parent
            # We treat it as alias, and use alias which it parent sends us
            if list(config.keys()) == [resource_constants.RESOURCE]:
                self.set_alias(resource, self.get_alias(parent_resource))

            config = {**parent_config, **config}

        self.set_config(resource, config)

        return config

    def resolve_resources(self):

        self.globals = self.resource_map.get(resource_constants.GLOBALS, {})

        for resource in self.resource_map:
            if resource in self.resource_config:
                continue

            self.resolve(resource)
