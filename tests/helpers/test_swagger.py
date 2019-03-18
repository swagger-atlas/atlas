from unittest import mock

import pytest

from atlas.modules.helpers import open_api_reader, swagger


class TestValidation:

    def test_validate(self, capsys):
        specs = open_api_reader.SpecsFile().inp_file_load()
        validator = swagger.Swagger(specs)
        validator.validate()

        captured = capsys.readouterr()

        assert captured.out == ""


class TestSwagger:

    @pytest.fixture
    def instance(self):
        instance = swagger.Swagger({})
        instance.writer = mock.MagicMock()
        return instance

    def test_validate_path_no_specs(self, instance):

        instance.validate_path()
        assert instance.writer.error.call_count == 4

    def test_validate_consumes_no_consumer(self, instance):

        instance.validate_consumes()
        assert instance.writer.warning.call_count == 1

    def test_validate_parameters(self, instance):

        swagger.Parameter = mock.MagicMock()
        instance.validate_parameters([{}], "")

        assert instance.writer.error.call_count == 1


class TestOperation:

    def test_no_response(self):

        instance = swagger.Operation("url", "method", {})
        instance.writer = mock.MagicMock()

        instance.validate()

        assert instance.writer.error.call_count == 1

    def test_no_valid_response(self):
        instance = swagger.Operation("url", "method", {"responses": {"400": {}}})
        instance.writer = mock.MagicMock()
        swagger.Response = mock.MagicMock()

        instance.validate()

        assert instance.writer.error.call_count == 1
