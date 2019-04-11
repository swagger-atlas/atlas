from unittest import mock

import pytest

from atlas.modules.transformer.open_api_models import Response, swagger_constants as constants, RESOURCES, DEF


class TestResponse:

    @pytest.fixture
    def instance(self):
        return Response()

    def test_get_properties_simple(self, instance):
        config = {constants.TYPE: constants.INTEGER}
        assert instance.get_properties(config) == config

    def test_get_properties_object(self, instance):
        config = {constants.TYPE: constants.OBJECT, constants.PROPERTIES: {"a": 1}}
        assert instance.get_properties(config) == {"a": 1}

    def test_get_properties_array(self, instance):
        config = {constants.TYPE: constants.ARRAY, constants.ITEMS: {"a": 1}}
        assert instance.get_properties(config) == {"a": 1}

    @mock.patch('atlas.modules.transformer.open_api_models.utils.get_ref_name')
    def test_get_definition_ref_with_ref(self, patched_ref_name, instance):
        patched_ref_name.return_value = "ref_1"

        assert instance.get_definition_ref({constants.REF: "some_ref"}) == "ref_1"

    def test_get_definition_ref_with_no_ref(self, instance):
        assert instance.get_definition_ref({}) is None

    def test_resolve_definitions_with_definitions(self, instance):
        instance.specs = {
            constants.DEFINITIONS: {
                "def_1": {}
            }
        }
        instance.parse_definitions = mock.MagicMock()
        instance.resolve_nested_definition = mock.MagicMock(return_value="a")
        instance.definitions = {"def_1": {}}

        instance.resolve_definitions()

        assert instance.definitions == {"def_1": {RESOURCES: "a"}}

    def test_resolve_definitions_with_no_definitions(self, instance):
        instance.specs = {
            constants.DEFINITIONS: {}
        }
        instance.parse_definitions = mock.MagicMock()
        instance.resolve_nested_definition = mock.MagicMock(return_value="a")
        instance.definitions = {"def_1": {}}

        instance.resolve_definitions()

        assert instance.definitions == {"def_1": {}}

    def test_parse_field_config_with_resource(self, instance):
        instance.get_properties = mock.MagicMock(return_value={
            constants.RESOURCE: "res"
        })
        instance.definitions = {"name": {RESOURCES: set(), DEF: set()}}
        instance.get_definition_ref = mock.MagicMock(return_value=None)

        instance.parse_field_config("name", {})

        assert instance.definitions == {"name": {RESOURCES: {"res"}, DEF: set()}}

    def test_parse_field_config_with_ref(self, instance):
        instance.get_properties = mock.MagicMock(return_value={})
        instance.definitions = {"name": {RESOURCES: set(), DEF: set()}}
        instance.get_definition_ref = mock.MagicMock(return_value="ref")

        instance.parse_field_config("name", {})

        assert instance.definitions == {"name": {RESOURCES: set(), DEF: {"ref"}}}
