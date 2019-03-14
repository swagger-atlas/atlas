from unittest import mock

import pytest

from atlas.modules import utils, exceptions, constants


class TestGetRefPathArray:

    def test_local_reference(self):
        assert utils.get_ref_path_array("#/definition/Sample") == ["definition", "Sample"]

    def test_external_reference(self):
        with pytest.raises(exceptions.ImproperSwaggerException):
            utils.get_ref_path_array("document.json#/sample")


class TestGetRefName:

    @mock.patch('atlas.modules.utils.get_ref_path_array')
    def test_get_ref_name(self, patched_ref_array):
        patched_ref_array.return_value = ["def", "abc"]

        assert utils.get_ref_name("#/def/abc") == "abc"
        patched_ref_array.assert_called_with("#/def/abc")


@mock.patch('atlas.modules.utils.get_ref_path_array')
class TestResolveReference:

    def test_no_reference(self, patched_ref_array):
        patched_ref_array.return_value = []
        specs = {"a": 1}

        assert utils.resolve_reference(specs, "definition") == specs

        patched_ref_array.assert_called_with("definition")

    def test_valid_reference(self, patched_ref_array):

        patched_ref_array.return_value = ["a"]
        specs = {"a": {"b": 1}}

        assert utils.resolve_reference(specs, "definition") == {"b": 1}

        patched_ref_array.assert_called_with("definition")

    def test_valid_reference_with_recursion(self, patched_ref_array):
        patched_ref_array.return_value = ["a", "b"]
        specs = {"a": {"b": 1}}

        assert utils.resolve_reference(specs, "definition") == 1

        patched_ref_array.assert_called_with("definition")

    def test_invalid_reference(self, patched_ref_array):
        patched_ref_array.return_value = ["a", "c"]
        specs = {"a": {"b": 1}}

        with pytest.raises(exceptions.ImproperSwaggerException):
            utils.resolve_reference(specs, "definition")


class TestConvertToSnakeCase:

    def test_with_camel_case(self):
        assert utils.convert_to_snake_case("camelCase") == "camel_case"

    def test_with_pascal_case(self):
        assert utils.convert_to_snake_case("CamelCase") == "camel_case"

    def test_with_normal_string(self):
        assert utils.convert_to_snake_case("magic") == "magic"

    def test_with_hybrid_string(self):
        assert utils.convert_to_snake_case("abc_caseLetter") == "abc_case_letter"


class TestGetProjectPath:

    @mock.patch('atlas.modules.utils.os')
    def test_get_project_path(self, patched_os):
        patched_os.getcwd.return_value = "path"
        assert utils.get_project_path() == "path"


class TestOperationIDName:

    def test_delete_method(self):
        assert utils.operation_id_name("x/{id}/y/{id}", constants.DELETE) == "x_PARAM_1_y_PARAM_2_delete"

    def test_create_method(self):
        assert utils.operation_id_name("x/{id}/y", constants.POST) == "x_PARAM_1_y_create"

    def test_list_method(self):
        assert utils.operation_id_name("x/{id}/y", constants.GET) == "x_PARAM_1_y_list"

    def test_read_method(self):
        assert utils.operation_id_name("x/{id}/y/{id}", constants.GET) == "x_PARAM_1_y_PARAM_2_read"

    def test_update_method(self):
        assert utils.operation_id_name("x/{id}/y/{id}", constants.PUT) == "x_PARAM_1_y_PARAM_2_update"

    def test_patch_method(self):
        assert utils.operation_id_name("x/{id}/y/{id}", constants.PATCH) == "x_PARAM_1_y_PARAM_2_partial_update"


class TestExtractResourceNameFromParam:

    def test_with_suffix(self):
        assert utils.extract_resource_name_from_param("pet_id", "") == "pet"

    def test_without_suffix_with_query_params(self):
        assert utils.extract_resource_name_from_param("id", "x/{id}/y/{y_id}/z/{abc}", constants.QUERY_PARAM) is None

    def test_without_suffix_with_path_params_not_in_settings_identifier(self):
        assert utils.extract_resource_name_from_param("abc", "x/{id}/y/{y_id}/z/{abc}", constants.PATH_PARAM) is None

    def test_without_suffix_with_path_params(self):
        assert utils.extract_resource_name_from_param("id", "x/{id}/y/{y_id}/z/{abc}", constants.PATH_PARAM) == "x"

    def test_without_suffix_with_first_resource(self):
        assert utils.extract_resource_name_from_param("id", "{id}/y/{y_id}/z/{abc}", constants.PATH_PARAM) is None

    def test_without_suffix_with_singular(self):
        assert utils.extract_resource_name_from_param("id", "pets/{id}/y/{y_id}/z/{abc}", constants.PATH_PARAM) == "pet"
