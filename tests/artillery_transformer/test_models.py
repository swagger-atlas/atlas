from unittest import mock

import pytest

from atlas.modules.transformer.base.models import ResourceFieldMap
from atlas.modules.transformer.artillery.models import Task, constants
from atlas.modules.transformer import interface


class TestTask:

    @pytest.fixture(scope='class')
    def open_api(self):
        return interface.OpenAPITaskInterface()

    @pytest.fixture
    def instance(self, open_api):
        return Task(open_api)

    @staticmethod
    def set_tag_value(value, instance):
        tag_check = mock.PropertyMock(return_value=value)
        type(instance).tag_check = tag_check
        return instance

    def test_body_definition_have_dependent_resources(self, instance):
        instance.open_api_op.dependent_resources = ['abc', 'xyz']
        assert "provider.getRelatedResources(['abc', 'xyz']);" in instance.body_definition()

    def test_body_with_headers(self, instance):
        instance.error_template_list = mock.MagicMock(return_value=['error'])
        instance.headers = ["'head_1': {}", "'head_2': {'a': 1}"]

        body = instance.body_definition()

        assert "let header_config = {'head_1': {}, 'head_2': {'a': 1}};" in body
        assert (
            mock.call(["_.merge(headers, provider.resolveObject(header_config));"])
            in instance.error_template_list.mock_calls
        )
        assert 'error' in body

    def test_body_with_no_data_body(self, instance):
        instance.error_template_list = mock.MagicMock(return_value=['error'])
        instance.data_body = dict()
        instance.open_api_op.method = constants.POST

        instance.body_definition()

        assert (
            mock.call(["body = provider.resolveObject(bodyConfig);"])
            not in instance.error_template_list.mock_calls
        )

    def test_body_with_delete_url_resource(self, instance):
        instance.delete_url_resource = ResourceFieldMap('resource', 'name')

        assert (
            "context.vars._delete_resource = { resource: 'resource', value: urlConfig[1].name };"
            in instance.body_definition()
        )

    def test_handle_mime_with_files(self, instance):
        instance.has_files = mock.MagicMock(return_value=True)
        assert "let formData = {};" in instance.handle_mime([])

    def test_cache_operation_tasks_with_no_response(self, instance):
        instance.parse_responses = mock.MagicMock(return_value=None)
        instance.post_check_tasks = []

        instance.cache_operation_tasks([])

        assert instance.post_check_tasks == []

    def test_set_yaml_definition_with_no_tags(self, instance):
        instance = self.set_tag_value(False, instance)
        instance.yaml_task = {}
        instance.open_api_op.method = constants.POST
        instance.open_api_op.url = "url"
        instance.before_func_name = "beforeFunc"
        instance.after_func_name = "afterFunc"

        instance.set_yaml_definition()

        assert instance.yaml_task == {
            constants.POST: {
                "url": "url",
                "beforeRequest": "beforeFunc",
                "afterResponse": "afterFunc"
            }
        }

    def test_set_yaml_definition_with_tags(self, instance):
        instance = self.set_tag_value(True, instance)
        instance.yaml_task = {}
        instance.open_api_op.method = constants.POST
        instance.open_api_op.url = "url"
        instance.before_func_name = "beforeFunc"
        instance.after_func_name = "afterFunc"
        instance.if_true_func_name = "ifTrueFunc"

        instance.set_yaml_definition()

        assert instance.yaml_task == {
            constants.POST: {
                "url": "url",
                "beforeRequest": "beforeFunc",
                "afterResponse": "afterFunc",
                "ifTrue": "ifTrueFunc"
            }
        }

    def test_convert_with_no_tags(self, instance):
        instance = self.set_tag_value(False, instance)

        statements = instance.convert(0)
        assert len(statements) == 2

    def test_convert_with_tags(self, instance):
        instance = self.set_tag_value(True, instance)

        statements = instance.convert(0)
        assert len(statements) == 3
