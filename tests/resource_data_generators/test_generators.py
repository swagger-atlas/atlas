from unittest import mock

import pytest

from atlas.modules.resource_data_generator.generators import (
    exceptions,
    ProfileResourceDataGenerator,
    resource_constants as constants,
    settings
)


class TestProfileResourceDataGenerator:
    """
    Test normal working of Profile Resource Generator
    """

    @mock.patch('atlas.modules.resource_data_generator.generators.db_client.Client')
    def test_db_client_queries(self, db_patch):

        db_obj = db_patch.return_value
        db_obj.fetch_ids.return_value = [1, 2]
        db_obj.fetch_rows.return_value = [3, 4]

        obj = ProfileResourceDataGenerator()
        obj.write_file = mock.MagicMock()

        obj.parse()

        db_obj.fetch_rows.assert_called_with(sql="some dummy sql", mapper=mock.ANY)
        assert db_obj.fetch_ids.mock_calls == [
            mock.call(sql="select name from t1 where abc = 1 limit 50;", mapper=mock.ANY),
            mock.call(sql="select id from t2 where active = True limit 50;", mapper=mock.ANY),
            mock.call(sql="select id from t4 where active = True limit 50;", mapper=mock.ANY)
        ]

    @mock.patch('atlas.modules.resource_data_generator.generators.db_client.Client')
    def test_resources_fetched(self, db_patch):
        db_obj = db_patch.return_value
        db_obj.fetch_ids.return_value = [1, 2]
        db_obj.fetch_rows.return_value = [3, 4]

        obj = ProfileResourceDataGenerator()
        obj.write_file = mock.MagicMock()

        obj.parse()

        expected_resources = {
            "simple": set(), "sql": {3, 4}, "construct_sql": {1, 2}, "minimal_construct_sql": {1, 2},
            "inherit_override": {1, 2}, "data_from_func": {7, 8}
        }

        write_args, _ = obj.write_file.call_args
        assert expected_resources in write_args


class TestProfileResourceDataGeneratorUnit:
    """
    Unit Test cases to test the edge cases of ProfileResourceDataGenerator
    Normal behaviour is already tested
    """

    @pytest.fixture
    def instance(self):
        return ProfileResourceDataGenerator()

    def test_parse_for_profile_incorrect_source(self, instance):
        with pytest.raises(exceptions.ResourcesException):
            instance.parse_for_resource("a", {"source": "some"})

    def test_parse_for_profile_result_return(self, instance):
        instance.parse_db_source = mock.MagicMock(return_value='abc')

        with pytest.raises(exceptions.ResourcesException):
            instance.parse_for_resource("abc", {})

    def test_construct_query_table_not_defined(self, instance):
        instance.construct_fetch_query = mock.MagicMock()

        with pytest.raises(exceptions.ResourcesException):
            instance.construct_query({}, {})

    def test_get_function_from_mapping_file_func_not_defined(self, instance):
        with pytest.raises(exceptions.ResourcesException):
            instance.get_function_from_mapping_file("func_not_exist")

    def test_parse_python_source_no_func_name(self, instance):
        with pytest.raises(exceptions.ResourcesException):
            instance.parse_python_source({})

    def test_parse_python_source_args_invalid_format(self, instance):
        instance.get_function_from_mapping_file = mock.MagicMock()

        with pytest.raises(exceptions.ResourcesException):
            instance.parse_python_source({"func": "some_func", "args": "invalid_args"})

    def test_parse_python_source_kwargs_invalid_format(self, instance):
        instance.get_function_from_mapping_file = mock.MagicMock()

        with pytest.raises(exceptions.ResourcesException):
            instance.parse_python_source({"func": "some_func", "kwargs": "invalid_args"})

    def test_parse_db_source_with_mapper(self, instance):
        instance.client.fetch_ids = mock.MagicMock()
        instance.get_function_from_mapping_file = mock.MagicMock(return_value="ret_func")
        instance.construct_query = mock.MagicMock(return_value="sql")
        instance.active_profile_config = {}

        instance.parse_db_source({"mapper": "func"}, {})

        instance.get_function_from_mapping_file.assert_called_once_with("func")
        instance.client.fetch_ids.assert_called_once_with(sql="sql", mapper="ret_func")

    def test_read_for_profile_duplicate_resources(self, instance):
        instance.parse_for_resource = mock.MagicMock()
        instance.resource_map_resolver.resource_map = {"res_a": "abc"}

        instance.read_for_profile({"res_1": {}, "res_a": {}})

        instance.parse_for_resource.assert_not_called()

    def test_read_for_profile_update_run_time(self, instance):
        instance.parse_for_resource = mock.MagicMock()
        instance.resource_map_resolver.resource_map = {"res_a": "abc", "res_b": "def"}
        instance.resource_map_resolver.alias_map = {}
        instance.resource_map_resolver.resource_config = {
            "res_a": {constants.RESOURCE_UPDATE_RUN_TIME: True}, "res_b": {constants.RESOURCE_UPDATE_RUN_TIME: False}
        }

        instance.read_for_profile({})

        assert settings.NOT_UPDATE_RUN_TIME_RESOURCES == {"res_b"}

    def test_get_profiles_with_existing_profiles(self, instance):
        instance.read_file_from_input = mock.MagicMock(return_value={"a": {}, "b": {}})
        instance.profiles = ["b", "c"]

        assert instance.get_profiles() == {"b": {}}
