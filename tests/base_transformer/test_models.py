from unittest import mock

import pytest

from atlas.modules.transformer.base.models import (
    ResourceFieldMap, TaskSet, Task,
    constants, exceptions, interface
)


class TestTaskSet:

    def test_set_scenarios_no_scenario(self):
        task_set = TaskSet([])
        assert task_set.scenarios == {"default": []}

    def test_set_scenarios_scenarios_with_default(self):
        scenarios = {"scene_a": {}, "default": {"a": 1}}
        task_set = TaskSet([], scenarios)
        assert task_set.scenarios == scenarios

    def test_set_scenarios_scenarios_with_no_default(self):
        scenarios = {"scene_a": {}, "scene_b": {}}
        task_set = TaskSet([], scenarios)
        assert task_set.scenarios == {**scenarios, "default": []}

    def test_convert_raises_error(self):
        task_set = TaskSet([])
        with pytest.raises(NotImplementedError):
            task_set.convert(1)


# Too many methods. Unit test class may have several methods, which is fine
# pylint: disable=R0904
class TestTask:

    @pytest.fixture(scope='class')
    @mock.patch('atlas.modules.transformer.base.models.Task.normalize_function_name')
    @mock.patch('atlas.modules.transformer.base.models.Task.parse_parameters')
    def instance(self, patched_params, patched_normalize_func_name):
        patched_normalize_func_name.return_value = "func_name"
        patched_params.return_value = None

        open_api = interface.OpenAPITaskInterface()

        return Task(open_api)

    def test_has_files_with_no_data_body(self, instance):
        instance.data_body = {}
        assert not instance.has_files()

    def test_has_files_with_data_body_no_files(self, instance):
        instance.data_body = {"a": {}, "b": {}}
        assert not instance.has_files()

    def test_has_files_with_data_with_files(self, instance):
        instance.data_body = {"a": {}, "b": {constants.TYPE: constants.FILE}}
        assert instance.has_files()

    def test_convert_raises_error(self, instance):
        with pytest.raises(NotImplementedError):
            instance.convert(1)

    def test_parse_body_params_with_schema(self, instance):
        config = {constants.SCHEMA: {"a": 1}}
        instance.data_body = {}

        instance.parse_body_params("name", config)

        assert instance.data_body == {"a": 1}

    def test_parse_body_params_without_schema_without_required(self, instance):
        config = {constants.REQUIRED: False}
        instance.data_body = {}

        instance.parse_body_params("name", config)

        assert instance.data_body == {}

    def test_parse_body_params_without_schema_with_required(self, instance):
        config = {constants.REQUIRED: True}
        instance.data_body = {}

        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.parse_body_params("name", config)

    def test_parse_header_params_with_config(self, instance):
        instance.schema_resolver.resolve = mock.MagicMock(return_value={"name": 3})
        instance.headers = []

        instance.parse_header_params("name", {"b": 1})

        instance.schema_resolver.resolve.assert_called_once_with({"name": {"b": 1}})
        assert instance.headers == ["'name': 3"]

    def test_parse_header_params_without_config(self, instance):
        instance.schema_resolver.resolve = mock.MagicMock(return_value={})
        instance.headers = []

        instance.parse_header_params("name", {"b": 1})

        instance.schema_resolver.resolve.assert_called_once_with({"name": {"b": 1}})
        assert instance.headers == []

    def test_parse_url_params_no_type(self, instance):
        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.parse_url_params("name", {})

    def test_parse_url_params_invalid_type(self, instance):
        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.parse_url_params("name", {constants.TYPE: constants.BODY_PARAM})

    def test_parse_url_params_query_params_with_optional(self, instance):
        instance.schema_resolver.resolve = mock.MagicMock()

        instance.parse_url_params("name", {constants.TYPE: constants.STRING, constants.REQUIRED: False}, "query")

        instance.schema_resolver.resolve.assert_not_called()

    def test_parse_url_params_query_params_with_positive_integer_params(self, instance):
        instance.schema_resolver.resolve = mock.MagicMock(return_value=None)

        config = {constants.TYPE: constants.STRING, constants.REQUIRED: True}
        instance.parse_url_params("page", config, "query")

        instance.schema_resolver.resolve.assert_called_once_with({"page": {
            constants.TYPE: constants.STRING, constants.REQUIRED: True, constants.MINIMUM: 1
        }})

    def test_parse_url_params_for_delete(self, instance):

        instance.open_api_op.method = constants.DELETE
        instance.schema_resolver.resolve = mock.MagicMock(return_value={"name": {constants.RESOURCE: "a"}})
        instance.open_api_op.url_end_parameter = mock.MagicMock(return_value="name")
        instance.url_params = {}
        instance.delete_url_resource = None

        config = {constants.TYPE: constants.STRING, constants.REQUIRED: True, constants.PARAMETER_NAME: "param"}
        instance.parse_url_params("name", config)

        instance.schema_resolver.resolve.assert_called_once_with({"name": {
            constants.TYPE: constants.STRING, constants.REQUIRED: True, constants.PARAMETER_NAME: "param",
        }})

        assert instance.delete_url_resource == ResourceFieldMap('a', 'name')
        assert instance.url_params == {"name": ("query", {"resource": "a", "options": {"delete": 1}})}

    def test_parse_url_params_without_delete(self, instance):

        instance.open_api_op.method = constants.DELETE
        instance.schema_resolver.resolve = mock.MagicMock(return_value={"name": {constants.RESOURCE: "a"}})
        instance.open_api_op.url_end_parameter = mock.MagicMock(return_value="no_name")
        instance.url_params = {}
        instance.delete_url_resource = None

        config = {constants.TYPE: constants.STRING, constants.REQUIRED: True, constants.PARAMETER_NAME: "param"}
        instance.parse_url_params("name", config)

        instance.schema_resolver.resolve.assert_called_once_with({"name": {
            constants.TYPE: constants.STRING, constants.REQUIRED: True, constants.PARAMETER_NAME: "param",
        }})

        assert instance.delete_url_resource is None
        assert instance.url_params == {"name": ("query", {"resource": "a"})}

    def test_parse_url_params_for_body_with_no_url_params(self, instance):

        instance.url_params = {}
        assert instance.parse_url_params_for_body() == ("{}", "{}")

    def test_parse_url_params_for_body_with_query_params(self, instance):

        instance.url_params = {"q_1": ["query", {"a": 1}], "q_2": ["query", {"b": 2}]}
        assert instance.parse_url_params_for_body() == (
            "{'q_1': {'a': 1}, 'q_2': {'b': 2}}",
            "{}"
        )

    def test_parse_url_params_for_body_with_path_params(self, instance):

        instance.url_params = {"p_1": ["path", {"a": 1}], "p_2": ["path", {"b": 2}]}
        assert instance.parse_url_params_for_body() == (
            "{}",
            "{'p_1': {'a': 1}, 'p_2': {'b': 2}}"
        )

    def test_parse_url_params_for_body_with_query_path_params(self, instance):

        instance.url_params = {"p_1": ["path", {"a": 1}], "q_1": ["query", {"b": 2}]}
        assert instance.parse_url_params_for_body() == (
            "{'q_1': {'b': 2}}",
            "{'p_1': {'a': 1}}"
        )

    def test_get_response_properties_with_properties(self, instance):
        instance.schema_resolver.resolve_with_read_only_fields = mock.MagicMock(return_value={"a": 1})
        assert instance.get_response_properties({}) == {"a": 1}

    def test_get_response_properties_without_properties(self, instance):
        instance.schema_resolver.resolve_with_read_only_fields = mock.MagicMock(return_value={})
        assert instance.get_response_properties({}) == {}


def test_normalize_function_name():
    open_api = interface.OpenAPITaskInterface()
    with pytest.raises(NotImplementedError):
        Task(open_api)


class TestTaskParseParameters:

    @pytest.fixture(scope='class')
    @mock.patch('atlas.modules.transformer.base.models.Task.normalize_function_name')
    def instance(self, patched_normalize_function_name):
        patched_normalize_function_name.return_value = ""
        open_api = interface.OpenAPITaskInterface()
        return Task(open_api)

    def test_no_parameters(self, instance):
        instance.parse_parameters({})
        assert instance.data_body == {}
        assert instance.headers == []
        assert instance.url_params == {}

    def test_config_with_no_in_raises_error(self, instance):
        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.parse_parameters({"param_1": {"name": "name", "type": "string", "required": True}})

    def test_config_with_no_name_raises_error(self, instance):
        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.parse_parameters({"param_1": {"in": "path", "type": "string", "required": True}})

    def test_config_with_invalid_in_raises_error(self, instance):
        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.parse_parameters(
                {"param_1": {"in": "some_invalid", "type": "string", "required": True, "name": "name"}}
            )

    def test_config_with_path_params(self, instance):
        instance.parse_url_params = mock.MagicMock()
        instance.parse_parameters({"param_1": {"in": "path", "type": "string", "required": True, "name": "name"}})
        instance.parse_url_params.assert_called_once_with(
            "name", {"in": "path", "type": "string", "required": True, "name": "name"}, param_type="path"
        )

    def test_config_with_body_params(self, instance):
        instance.parse_body_params = mock.MagicMock()
        instance.parse_parameters({"param_1": {"in": "body", "type": "string", "required": True, "name": "name"}})
        instance.parse_body_params.assert_called_once_with(
            "name", {"in": "body", "type": "string", "required": True, "name": "name"}
        )

    def test_config_with_query_params(self, instance):
        instance.parse_url_params = mock.MagicMock()
        instance.parse_parameters({"param_1": {"in": "query", "type": "string", "required": True, "name": "name"}})
        instance.parse_url_params.assert_called_once_with(
            "name", {"in": "query", "type": "string", "required": True, "name": "name"}
        )

    def test_config_with_header_params(self, instance):
        instance.parse_header_params = mock.MagicMock()
        instance.parse_parameters({"param_1": {"in": "header", "type": "string", "required": True, "name": "name"}})
        instance.parse_header_params.assert_called_once_with(
            "name", {"in": "header", "type": "string", "required": True, "name": "name"}
        )

    def test_config_with_form_params(self, instance):
        instance.parse_header_params = mock.MagicMock()
        instance.data_body = {}
        instance.schema_resolver.resolve = mock.MagicMock(return_value={"name": {"type": "x"}})

        instance.parse_parameters({"param_1": {"in": "formData", "type": "string", "required": True, "name": "name"}})

        assert instance.data_body == {"name": {"type": "x"}}
        instance.schema_resolver.resolve.assert_called_once_with(
            {"name": {"in": "formData", "type": "string", "required": True, "name": "name"}}
        )

    @mock.patch('atlas.modules.transformer.base.models.utils.resolve_reference')
    def test_with_ref(self, patched_ref, instance):
        patched_ref.return_value = {"in": "formData", "type": "string", "required": True, "name": "name"}
        instance.schema_resolver.spec = "ref"
        instance.parse_parameters({"param_1": {"$ref": "abc"}})

        patched_ref.assert_called_once_with("ref", "abc")


class TestTaskParseResponses:
    """
    Unit test cases for Task.parse_responses
    """

    @pytest.fixture(scope='class')
    @mock.patch('atlas.modules.transformer.base.models.Task.normalize_function_name')
    @mock.patch('atlas.modules.transformer.base.models.Task.parse_parameters')
    def instance(self, patched_params, patched_normalize_func_name):
        patched_normalize_func_name.return_value = "func_name"
        patched_params.return_value = None

        open_api = interface.OpenAPITaskInterface()

        return Task(open_api)

    def test_no_responses(self, instance):
        assert instance.parse_responses({}) == {}

    def test_default_code_with_response(self, instance):
        instance.get_response_properties = mock.MagicMock(return_value={"a": 1})

        assert instance.parse_responses({constants.DEFAULT: {"name": "n"}}) == {"a": 1}
        instance.get_response_properties.assert_called_once_with({"name": "n"})

    def test_default_code_with_no_response(self, instance):
        instance.get_response_properties = mock.MagicMock(return_value=None)

        assert instance.parse_responses({constants.DEFAULT: {"name": "n"}}) == {}
        instance.get_response_properties.assert_called_once_with({"name": "n"})

    def test_invalid_status_code(self, instance):
        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.parse_responses({"status": {"name": "n"}})

    def test_status_with_error_codes(self, instance):
        assert instance.parse_responses({400: {"name": "n"}, "401": {"name": "n"}}) == {}

    def test_status_with_valid_status_no_schema(self, instance):
        instance.get_response_properties = mock.MagicMock(return_value={})
        assert instance.parse_responses({200: {"name": "n"}}) == {}

    def test_status_with_valid_status_with_schema(self, instance):
        instance.get_response_properties = mock.MagicMock(return_value={"a": 1})
        assert instance.parse_responses({200: {"name": "n"}}) == {"a": 1}
