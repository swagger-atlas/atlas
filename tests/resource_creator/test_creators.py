from unittest import mock

import pytest

from atlas.modules.resource_creator.creators import AutoGenerator, swagger_constants, exceptions, settings


class TestAutoGeneratorBehaviour:
    """
    System test for basic functionality of Auto Generator
    More complex use cases would be covered via Unit Tests
    """

    def test_new_resource_are_created(self):
        instance = AutoGenerator()
        instance.parse()
        assert instance.new_resources == {"pet", "category"}

    def test_resources_are_inserted_in_swagger(self):
        instance = AutoGenerator()
        instance.parse()
        assert instance.specs["paths"]["/pet/{petId}"]["get"]["parameters"][0].get("resource") == "pet"
        assert instance.specs["definitions"]["Category"]["properties"]["id"].get("resource") == "category"
        assert instance.specs["definitions"]["Pet"]["properties"]["id"].get("resource") == "pet"


# Too many methods. Unit test class may have several methods, which is fine
# pylint: disable=R0904
class TestAutoGeneratorUnit:
    """
    Unit test cases for Auto generator
    Will only cover corner-cases and exceptions, since general behaviour is already covered in System test cases
    """

    @pytest.fixture(scope="class")
    def instance(self):
        return AutoGenerator()

    def test_format_reference(self, instance):
        assert instance.format_references({"abc", "MA-jo-rs", "Cr_eA-te"}) == {"abc", "majors", "create"}

    def test_add_resource_with_blank(self, instance):
        old_resources = instance.resource_keys
        assert instance.add_resource(None) == ""
        assert instance.resource_keys == old_resources

    def test_add_resource_with_existing(self, instance):
        instance.resource_keys.add("some")
        len_resources = len(instance.resource_keys)
        assert instance.add_resource("Some") == "some"
        assert len(instance.resource_keys) == len_resources

    def test_add_resource_with_new(self, instance):
        instance.resource_keys -= {"example"}
        assert instance.add_resource("example") == "example"
        assert "example" in instance.resource_keys
        assert "example" in instance.new_resources

    def test_add_reference_definition_already_processed(self, instance):
        old_definitions = instance.specs.get(swagger_constants.DEFINITIONS, {})
        instance.processed_refs.add("cree")
        instance.add_reference_definition("cree", {})
        assert instance.specs.get(swagger_constants.DEFINITIONS, {}) == old_definitions

    def test_add_reference_definition_already_exists(self, instance):
        old_definitions = instance.specs.get(swagger_constants.DEFINITIONS, {})
        instance.add_reference_definition("pet", {})
        assert instance.specs.get(swagger_constants.DEFINITIONS, {}) == old_definitions

    def test_add_reference_definition_new_definition(self, instance):
        instance.add_reference_definition("new", {"a": "bcd", "name": "some"})
        assert instance.specs.get(swagger_constants.DEFINITIONS, {}).get("new", {}) == {
            "type": "object",
            "properties": {
                "some": {
                    "a": "bcd",
                    "name": "some"
                }
            }
        }

    @mock.patch('atlas.modules.resource_creator.creators.utils.extract_resource_name_from_param')
    def test_extract_resource_name_from_param_resource_name_exists(self, patch, instance):
        patch.return_value = "exists"
        assert instance.extract_resource_name_from_param("param_name", "url_path") == "exists"

    @mock.patch('atlas.modules.resource_creator.creators.utils.extract_resource_name_from_param')
    def test_extract_resource_name_from_param_resource_name_not_exists(self, patch, instance):
        patch.return_value = None
        assert instance.extract_resource_name_from_param("param_name", "url_path") is None

    @mock.patch('atlas.modules.resource_creator.creators.utils.extract_resource_name_from_param')
    def test_extract_resource_name_from_param_resource_name_not_exists_but_is_in_resource_keys(self, patch, instance):
        patch.return_value = None
        instance.resource_keys.add("param_name")
        assert instance.extract_resource_name_from_param("param_name", "url_path") == "param_name"
        instance.resource_keys.remove("param_name")     # Clean up

    def test_parse_params_no_params(self, instance):
        assert instance.parse_params([], "url") == set()
        assert instance.resource_params == set()

    def test_parse_params_invalid_param(self, instance):
        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.parse_params([{}], "url")

    def test_parse_params_path_param_returns_resource(self, instance):
        instance.extract_resource_name_from_param = mock.MagicMock(return_value='res')
        param = {"in": "path", "name": "xyz"}
        assert instance.parse_params([param], "url") == {"res"}
        assert instance.resource_params == {"res"}
        assert param.get("resource") == "res"
        assert instance.specs.get(swagger_constants.DEFINITIONS, {}).get("res") is not None

    def test_parse_params_path_param_not_return_resource(self, instance):
        instance.extract_resource_name_from_param = mock.MagicMock(return_value='')
        param = {"in": "path", "name": "xyz"}
        assert instance.parse_params([param], "url") == set()
        assert instance.resource_params == set()
        assert param.get("resource") is None

    def test_parse_params_path_param_has_resource(self, instance):
        param = {"in": "path", "name": "xyz", "resource": "path_res"}
        assert instance.parse_params([param], "url") == {"pathres"}
        assert instance.resource_params.issuperset({"pathres"})

    def test_parse_params_multi_params(self, instance):
        instance.extract_resource_name_from_param = mock.MagicMock(return_value='')
        assert instance.parse_params(
            [{"in": "path", "name": "a"}, {"in": "body", "name": "b"}, {"in": "form", "name": "c"}], "url"
        ) == set()
        assert instance.resource_params == set()

    @mock.patch('atlas.modules.resource_creator.creators.utils.resolve_reference')
    def test_params_params_with_ref(self, patch, instance):
        patch.return_value = {"in": "path", "name": "xyz"}
        instance.extract_resource_name_from_param = mock.MagicMock(return_value='patched_res')
        assert instance.parse_params([{"$ref": "param"}], "url") == {"patchedres"}
        assert instance.resource_params.issuperset({"patchedres"})

    def test_parse_reference_with_all_of(self, instance):
        config = {
            "allOf": [
                {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer"
                        }
                    }
                },
                {
                    "type": "string"
                },
                {
                    "$ref": "#/definitions/Pet"
                }
            ]
        }
        instance.parse_reference("all_of_test", config)
        assert instance.processed_refs.issuperset({"all_of_test"})
        assert instance.resource_params.issuperset({"alloftest"})

    @mock.patch('atlas.modules.resource_creator.creators.utils.resolve_reference')
    def test_invalid_ref(self, patch, instance):
        instance.get_ref_name_and_config(123)
        patch.assert_not_called()

    @staticmethod
    def parse_params_side_effect(*args):
        return {args[0][0].get("name")}

    def test_parse_with_common_parameters(self, instance):
        instance.parse_params = mock.MagicMock(side_effect=self.parse_params_side_effect)
        instance.specs["paths"]["/pet"]["parameters"] = [{"name": "dummy", "in": "xyz"}]
        instance.parse()
        assert instance.specs["paths"]["/pet/{petId}"]["get"].get(swagger_constants.DEPENDENT_RESOURCES) is None
        assert instance.specs["paths"]["/pet"]["post"].get(swagger_constants.DEPENDENT_RESOURCES) == {"dummy", "body"}

    def test_parse_with_no_parameters(self, instance):
        instance.parse_params = mock.MagicMock(side_effect=self.parse_params_side_effect)
        instance.specs["paths"]["/pet/{petId}"]["parameters"] = [{"name": "dummy", "in": "xyz"}]
        instance.specs["paths"]["/pet/{petId}"]["get"]["parameters"] = []
        instance.parse()
        assert instance.specs["paths"]["/pet/{petId}"]["get"].get(swagger_constants.DEPENDENT_RESOURCES) is None

    @mock.patch('atlas.modules.resource_creator.creators.utils.operation_id_name')
    def test_parse_with_no_op_id(self, patch, instance):
        patch.return_value = 'opId'
        instance.parse_params = mock.MagicMock(side_effect=self.parse_params_side_effect)
        instance.specs["paths"]["/pet/{petId}"]["get"][swagger_constants.OPERATION] = ""
        instance.parse()
        assert instance.specs["paths"]["/pet/{petId}"]["get"][swagger_constants.OPERATION] == "opId"

    def test_update(self, instance):
        instance.write_file_to_output = mock.MagicMock()
        instance.write_file_to_input = mock.MagicMock()
        res_map = {resource: {"def": "# Add your definition here"} for resource in instance.new_resources}

        instance.update()

        instance.write_file_to_output.assert_called_once_with(instance.swagger_file, instance.specs, append_mode=False)
        instance.write_file_to_input.assert_called_once_with(
            settings.MAPPING_FILE, {**instance.resource_map_resolver.resource_map, **res_map}, append_mode=False
        )
