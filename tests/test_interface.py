import pytest

from atlas.modules.transformer.interface import OpenAPITaskInterface, constants, exceptions


# Too many methods. Unit test class may have several methods, which is fine
# pylint: disable=R0904
class TestInterface:

    @pytest.fixture(scope='class')
    def instance(self):
        return OpenAPITaskInterface()

    def test_parameters(self, instance):
        instance.parameters = {"param_1": {}}
        assert instance.parameters == {"param_1": {}}

    def test_func_name(self, instance):
        instance.func_name = "abc.xyz"
        assert instance.func_name == "abc_xyz"

    def test_method(self, instance):
        instance.method = constants.POST
        assert instance.method == constants.POST

    def test_method_with_invalid_method(self, instance):
        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.method = "method"

    def test_url(self, instance):
        instance.url = "url"
        assert instance.url == "url"

    def test_tags(self, instance):
        instance.tags = ["tag_1"]
        assert instance.tags == ["tag_1"]

    def test_tags_with_invalid_values(self, instance):
        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.tags = "tags"

    def test_responses_with_no_values(self, instance):
        instance.responses = {}
        assert instance.responses == {}

    def test_responses_with_invalid_type(self, instance):
        with pytest.raises(exceptions.ImproperSwaggerException):
            instance.responses = {"resp": {}}

    def test_responses_with_responses(self, instance):
        instance.responses = {
            "400": {}, 200: {}, "default": {}
        }

        assert instance.responses == {"default": {}, "200": {}}

    def test_consume_no_values(self, instance):
        instance.consumes = []
        assert instance.consumes == [constants.JSON_CONSUMES]

    def test_consume_values(self, instance):
        instance.consumes = [constants.JSON_CONSUMES, constants.MULTIPART_CONSUMES, "some_consume"]
        assert instance.consumes == [constants.JSON_CONSUMES, constants.MULTIPART_CONSUMES]

    def test_url_end_parameter_no_parameter(self, instance):
        instance.url = "abc/xyz"
        assert instance.url_end_parameter() is None

    def test_url_end_parameter_with_parameter(self, instance):
        instance.url = "abc/{xyz}"
        assert instance.url_end_parameter() == "xyz"

    def test_dependent_resources(self, instance):
        instance.dependent_resources = {"abc"}
        assert instance.dependent_resources == {"abc"}

    def test_op_id(self, instance):
        instance.method = constants.POST
        instance.url = "url"

        assert instance.op_id == "POST url"

    def test_resource_producers(self, instance):
        instance.resource_producers = {"abc"}
        assert instance.resource_producers == {"abc"}

    def test_producer_references(self, instance):
        instance.producer_references = {"abc"}
        assert instance.producer_references == {"abc"}

    def test_mime_default(self, instance):
        instance.consumes = [constants.JSON_CONSUMES]
        assert instance.mime == constants.JSON_CONSUMES

    def test_mime_consumes(self, instance):
        instance.consumes = [constants.MULTIPART_CONSUMES, constants.JSON_CONSUMES, constants.FORM_CONSUMES]
        assert instance.mime == constants.JSON_CONSUMES
