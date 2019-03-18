from unittest import mock

import pytest

from atlas.modules.transformer.artillery.setup import ArtillerySetup


class TestPythonToJS:
    """
    Test Setup.convert_python_value_to_js_value function
    """

    @pytest.fixture(scope='class')
    @mock.patch('atlas.modules.transformer.artillery.setup.ArtillerySetup.create_folder')
    def instance(self, patched_method):
        patched_method.return_value = ""
        return ArtillerySetup()

    def test_string_with_stringify(self, instance):
        assert instance.convert_python_value_to_js_value("string", "variable", True) == "'string'"

    def test_string_without_stringify(self, instance):
        assert instance.convert_python_value_to_js_value("string", "variable", False) == "string"

    def test_bool_true(self, instance):
        assert instance.convert_python_value_to_js_value(True, "variable") == "true"

    def test_bool_false(self, instance):
        assert instance.convert_python_value_to_js_value(False, "variable") == "false"

    def test_num(self, instance):
        assert instance.convert_python_value_to_js_value(1, "variable") == 1

    def test_list(self, instance):
        assert instance.convert_python_value_to_js_value([1, 2], "variable") == [1, 2]

    def test_tuple(self, instance):
        assert instance.convert_python_value_to_js_value((1, 2), "variable") == [1, 2]

    def test_set(self, instance):
        assert instance.convert_python_value_to_js_value({1, 2}, "variable") == "new Set([1, 2])"

    def test_dict_with_items(self, instance):
        assert instance.convert_python_value_to_js_value({"a": 1, "b": [1, 2]}, "variable") == {"a": 1, "b": [1, 2]}

    def test_empty(self, instance):
        assert instance.convert_python_value_to_js_value(dict(), "variable") == {}

    def test_dict_with_functions(self, instance):
        assert instance.convert_python_value_to_js_value({"a": lambda x: x}, "variable") == {}

    def test_function(self, instance):
        assert instance.convert_python_value_to_js_value(lambda x: x, "variable") is None

    def test_object(self, instance):
        assert instance.convert_python_value_to_js_value(object(), "variable") is None


class DummyClass:
    """
    Dummy Class for testing purposes
    """

    def __str__(self):
        return "abc"

    def __init__(self):
        self.var = 1
        self.func_var = lambda x: x


class TestArtillerySetup:
    """
    Test Artillery Setup class
    Some individual functions are tested separately in thier own class
    """

    @pytest.fixture
    @mock.patch('atlas.modules.transformer.artillery.setup.ArtillerySetup.create_folder')
    def instance(self, patched_method):
        patched_method.return_value = ""
        return ArtillerySetup()

    def test_construct_js_statements_no_python_vars(self, instance):
        assert instance.construct_js_statements([], object()) == []

    def test_construct_js_statements(self, instance):
        py_object = DummyClass()
        assert instance.construct_js_statements(dir(py_object), py_object) == ["exports.var = 1;"]

    @mock.patch('atlas.modules.transformer.artillery.setup.open')
    def test_constants_file(self, patched_open, instance):
        instance.construct_js_statements = mock.MagicMock()

        instance.constants_file()

        instance.construct_js_statements.assert_called()
        patched_open.assert_called()

    @mock.patch('atlas.modules.transformer.artillery.setup.open')
    def test_settings_file(self, patched_open, instance):
        instance.construct_js_statements = mock.MagicMock()

        instance.settings_file()

        instance.construct_js_statements.assert_called()
        patched_open.assert_called()

    def test_setup(self, instance):
        instance.constants_file = mock.MagicMock()
        instance.settings_file = mock.MagicMock()

        instance.setup()

        instance.constants_file.assert_called()
        instance.settings_file.assert_called()

    @mock.patch('atlas.modules.transformer.artillery.setup.os')
    def test_create_folder_path_not_exist(self, patched_os):
        patched_os.path.exists.return_value = False
        patched_os.makedirs = mock.MagicMock()

        ArtillerySetup()

        assert patched_os.makedirs.call_count == 2

    @mock.patch('atlas.modules.transformer.artillery.setup.os')
    def test_create_folders_path_exists(self, patched_os):
        patched_os.path.exists.return_value = True
        patched_os.makedirs = mock.MagicMock()

        ArtillerySetup()

        patched_os.makedirs.assert_not_called()
