from copy import deepcopy

from atlas.conf import settings
from atlas.modules import constants


class ReferenceField:

    def __init__(self, name, config):
        self.name = name
        self.config = config

    @property
    def ref(self):
        return self.resolve_config().get(constants.REF)

    @property
    def resource(self):
        return self.resolve_config().get(constants.RESOURCE)

    @property
    def can_contain_primary_resource(self):
        """
        Determine whether this field can contain primary resource for this reference
        """

        return self.resource and self.name in settings.REFERENCE_FIELD_RESOURCES

    def resolve_config(self):
        config = deepcopy(self.config)
        _type = config.get(constants.TYPE)
        if _type == constants.ARRAY:
            config = config.get(constants.ITEMS, {})
        return config
