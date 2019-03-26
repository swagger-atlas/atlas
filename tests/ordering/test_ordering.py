from unittest import mock

from atlas.modules.transformer.ordering.ordering import Ordering


class TestOrderingConstructor:

    def test_with_interfaces(self):
        instance = Ordering(interfaces=["a"])
        assert instance.interfaces == ["a"]

    @mock.patch('atlas.modules.transformer.ordering.ordering.open_api_models')
    def test_without_interfaces(self, patched_specs):
        open_api = patched_specs.OpenAPISpec()
        open_api.get_interfaces = mock.MagicMock()

        instance = Ordering()
        assert instance.interfaces == open_api.interfaces
        open_api.get_interfaces.assert_called()
