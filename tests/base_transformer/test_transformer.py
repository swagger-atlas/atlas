import os
from unittest import mock

import pytest

from atlas.modules.transformer.base.models import TaskSet
from atlas.modules.transformer.base.transformer import (
    FileConfig, constants, exceptions, settings
)


class TestTransformer:

    @pytest.fixture
    def instance(self):
        task_set = TaskSet([])
        return FileConfig(task_set)

    def test_get_imports(self, instance):
        with pytest.raises(NotImplementedError):
            instance.get_imports()

    def test_get_global_vars(self, instance):
        assert instance.get_global_vars() == ""

    @mock.patch('atlas.modules.transformer.base.transformer.open')
    @mock.patch('atlas.modules.transformer.base.transformer.utils.get_project_path')
    def test_write_to_file_no_file_name_no_sub_path(self, patched_get_path, patched_open, instance):
        patched_get_path.return_value = ""
        instance.OUT_FILE = "out_file"
        instance.convert = mock.MagicMock()

        instance.write_to_file()

        patched_open.assert_called_once_with(os.path.join(settings.OUTPUT_FOLDER, "out_file"), 'w')

    @mock.patch('atlas.modules.transformer.base.transformer.open')
    @mock.patch('atlas.modules.transformer.base.transformer.utils.get_project_path')
    def test_write_to_file_with_file_name(self, patched_get_path, patched_open, instance):
        patched_get_path.return_value = ""
        instance.OUT_FILE = "out_file"
        instance.convert = mock.MagicMock()

        instance.write_to_file(file_name="xyz")

        patched_open.assert_called_once_with(os.path.join(settings.OUTPUT_FOLDER, "xyz"), 'w')

    @mock.patch('atlas.modules.transformer.base.transformer.open')
    @mock.patch('atlas.modules.transformer.base.transformer.utils.get_project_path')
    def test_write_to_file_with_sub_path(self, patched_get_path, patched_open, instance):
        patched_get_path.return_value = ""
        instance.OUT_FILE = "out_file"
        instance.convert = mock.MagicMock()

        instance.write_to_file(sub_path="sub")

        patched_open.assert_called_once_with(os.path.join(settings.OUTPUT_FOLDER, "sub", "out_file"), 'w')


def test_transformer_convert():
    task_set = TaskSet([])
    instance = FileConfig(task_set)
    instance.task_set = mock.MagicMock()
    instance.task_set.convert = mock.MagicMock(return_value="c")
    instance.get_imports = mock.MagicMock(return_value="a")
    instance.get_global_vars = mock.MagicMock(return_value="b")

    assert instance.convert() == "a\n\nb\n\nc"

    instance.get_imports.assert_called_once()
    instance.get_global_vars.assert_called_once()
    instance.task_set.convert.assert_called_once_with(width=1)


@mock.patch('atlas.modules.transformer.base.transformer.settings')
class TestTransformerGetSwaggerUrl:

    @pytest.fixture(scope='class')
    def instance(self):
        task_set = TaskSet([])
        return FileConfig(task_set)

    def test_server_protocol_server_host_server_api_url(self, patched_settings, instance):
        patched_settings.SERVER_URL = {
            "protocol": "http",
            "host": "localhost",
            "api_url": "/v1/api"
        }

        assert instance.get_swagger_url() == "http://localhost/v1/api"

    def test_specs_protocol(self, patched_settings, instance):
        patched_settings.SERVER_URL = {
            "protocol": "",
            "host": "localhost",
            "api_url": "/v1/api"
        }
        instance.specs = {
            constants.SCHEMES: ["https"]
        }

        assert instance.get_swagger_url() == "https://localhost/v1/api"

    def test_no_protocol(self, patched_settings, instance):
        patched_settings.SERVER_URL = {
            "protocol": "",
            "host": "localhost",
            "api_url": "/v1/api"
        }
        instance.specs = {
            constants.SCHEMES: []
        }

        assert instance.get_swagger_url() == "http://localhost/v1/api"

    def test_specs_host(self, patched_settings, instance):
        patched_settings.SERVER_URL = {
            "protocol": "http",
            "host": "",
            "api_url": "/v1/api"
        }
        instance.specs = {
            constants.HOST: "host"
        }

        assert instance.get_swagger_url() == "http://host/v1/api"

    def test_no_host(self, patched_settings, instance):
        patched_settings.SERVER_URL = {
            "protocol": "http",
            "host": "",
            "api_url": "/v1/api"
        }
        instance.specs = {}

        assert instance.get_swagger_url() == "http://localhost/v1/api"

    def test_specs_api_url_with_info(self, patched_settings, instance):
        patched_settings.SERVER_URL = {
            "protocol": "http",
            "host": "localhost",
            "api_url": ""
        }
        instance.specs = {
            constants.INFO: {
                constants.API_URL: "/api"
            }
        }

        assert instance.get_swagger_url() == "http://localhost/api"

    def test_specs_api_url_with_no_info_with_base_path(self, patched_settings, instance):
        patched_settings.SERVER_URL = {
            "protocol": "http",
            "host": "localhost",
            "api_url": ""
        }
        instance.specs = {
            constants.INFO: {},
            constants.BASE_PATH: "/base"
        }

        assert instance.get_swagger_url() == "http://localhost/base"

    def test_specs_api_url_with_no_info_with_no_base_path(self, patched_settings, instance):
        patched_settings.SERVER_URL = {
            "protocol": "http",
            "host": "localhost",
            "api_url": ""
        }
        instance.specs = {
            constants.INFO: {},
        }

        assert instance.get_swagger_url() == "http://localhost"

    def test_double_slash_raises_error(self, patched_settings, instance):
        patched_settings.SERVER_URL = {
            "protocol": "http",
            "host": "localhost/",
            "api_url": "/v1/api"
        }

        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.get_swagger_url()

    def test_no_raises_error(self, patched_settings, instance):
        patched_settings.SERVER_URL = {
            "protocol": "http",
            "host": "localhost",
            "api_url": "v1/api"
        }

        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.get_swagger_url()
