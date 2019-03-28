from copy import deepcopy

from atlas.conf import settings
from atlas.modules import constants


class ElementConfig:

    def __init__(self, config):
        self.config = config
        self.resolved_config = self.resolve_config()

    def resolve_config(self):
        config = deepcopy(self.config)
        _type = config.get(constants.TYPE)
        if _type == constants.ARRAY:
            config = config.get(constants.ITEMS, {})
        return config

    @property
    def ref(self):
        return self.resolved_config.get(constants.REF)


class ReferenceField(ElementConfig):

    def __init__(self, name, config):
        super().__init__(config=config)
        self.name = name

    @property
    def resource(self):
        return self.resolved_config.get(constants.RESOURCE)

    @property
    def can_contain_primary_resource(self):
        """
        Determine whether this field can contain primary resource for this reference
        """

        return self.resource and self.name in settings.SWAGGER_REFERENCE_FIELD_RESOURCE_IDENTIFIERS


class Schema:
    """
    Represents OpenAPI Schema Object
    https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#schemaObject
    """

    def __init__(self, schema_config, specs=None):
        self.config = schema_config
        self.specs = specs or {}

    def get_all_refs(self):
        """
        Just resolve Schema at top levels to get all refs
        """

        element = ElementConfig(self.config)
        if element.ref:
            return [element.ref]

        # Reference not found directly
        # It may be nested in Array and Object. Search there

        refs = []
        _type = self.config.get(constants.TYPE)

        props = {}
        if _type == constants.ARRAY:
            props = self.config.get(constants.ITEMS, {})
        elif _type == constants.OBJECT:
            props = self.config.get(constants.PROPERTIES, {})

        for element_config in props.values():
            element = ElementConfig(element_config)
            if element.ref:
                refs.append(element.ref)

        return refs
