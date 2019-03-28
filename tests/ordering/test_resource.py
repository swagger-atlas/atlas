from unittest import mock

import pytest

from atlas.modules.transformer.ordering.resource import (
    Resource, Reference, ResourceGraph, SwaggerResourceValidator,
    constants, exceptions
)
from atlas.modules.transformer.interface import OpenAPITaskInterface


class TestReference:

    @pytest.fixture
    def instance(self):
        return Reference(key="ref", config={})

    def test_resolve_primary_resource_no_candidates(self, instance):
        instance.associated_resources = {"res_1"}

        instance.resolve_primary_resource(set())

        assert instance.associated_resources == set()
        assert instance.primary_resource == "res_1"

    def test_resolve_primary_resource_with_candidates(self, instance):
        instance.associated_resources = {"res_1"}

        instance.resolve_primary_resource({"prim_res"})

        assert instance.associated_resources == {"res_1"}
        assert instance.primary_resource == "prim_res"

    def test_resolve_primary_resource_with_zero_candidates(self, instance):
        instance.associated_resources = set()

        instance.resolve_primary_resource(set())

        assert instance.primary_resource == "ref"

    def test_resolve_primary_resource_with_multiple_candidates(self, instance):
        instance.associated_resources = set()

        with pytest.raises(exceptions.ResourcesException):
            instance.resolve_primary_resource({"ref_1", "ref_2"})

    def test_get_connections_with_properties(self, instance):
        instance.resolve_primary_resource = mock.MagicMock()

        instance.config = {
            constants.PROPERTIES: {
                "name_1": {
                    constants.RESOURCE: "resource_1",
                    constants.REF: "ref_1"
                },
                "name_2": {},
                "id": {
                    constants.RESOURCE: "resource_3",
                    constants.REF: "ref_3"
                }
            }
        }

        instance.get_connections()

        assert instance.connected_refs == {"ref_1", "ref_3"}
        assert instance.associated_resources == {"resource_1", "resource_3"}
        instance.resolve_primary_resource.assert_called_once_with({"resource_3"})

    def test_get_connections_with_additional_properties(self, instance):
        instance.resolve_primary_resource = mock.MagicMock()

        instance.config = {
            constants.ADDITIONAL_PROPERTIES: {
                constants.RESOURCE: "resource_1",
                constants.REF: "ref_1"
            }
        }

        instance.get_connections()

        assert instance.connected_refs == {"ref_1"}
        assert instance.associated_resources == {"resource_1"}
        instance.resolve_primary_resource.assert_called_once_with(set())


class TestResource:

    @pytest.fixture(scope='class')
    def instance(self):
        return Resource(key="res")

    def test_add_consumer(self, instance):
        instance.add_consumer("op_1")
        assert instance.consumers == {"op_1"}

    def test_add_producer(self, instance):
        instance.add_producer("op_2")
        assert instance.producers == {"op_2"}

    def test_add_destructor(self, instance):
        instance.consumers = set()
        instance.add_destructor("op_3")
        assert instance.consumers == {"op_3"}
        assert instance.destructors == {"op_3"}


class TestResourceGraph:

    @pytest.fixture
    def instance(self):
        return ResourceGraph({})

    def test_get_associated_resource_for_ref(self, instance):
        ref = Reference(key="ref", config={})
        ref.primary_resource = "res"

        instance.references = {"ref": ref}

        assert instance.get_associated_resource_for_ref("ref") == "res"

    @mock.patch('atlas.modules.transformer.ordering.resource.utils.get_ref_name')
    def test_add_ref_edge_with_ref(self, patched_ref_name, instance):
        instance.get_associated_resource_for_ref = mock.MagicMock(return_value="res")
        instance.add_edge = mock.MagicMock()
        patched_ref_name.return_value = "source_ref"

        instance.add_ref_edge("ref", "d_key")

        patched_ref_name.assert_called_once_with("ref")
        instance.get_associated_resource_for_ref.assert_called_once_with("source_ref")
        instance.add_edge.assert_called_once_with("res", "d_key")

    @mock.patch('atlas.modules.transformer.ordering.resource.utils.get_ref_name')
    def test_add_ref_edge_with_no_ref(self, patched_ref_name, instance):
        instance.get_associated_resource_for_ref = mock.MagicMock(return_value="res")
        instance.add_edge = mock.MagicMock()
        patched_ref_name.return_value = "source_ref"

        instance.add_ref_edge(None, "d_key")

        patched_ref_name.assert_not_called()
        instance.get_associated_resource_for_ref.assert_not_called()
        instance.add_edge.assert_not_called()

    @mock.patch('atlas.modules.transformer.ordering.resource.utils.get_ref_name')
    def test_construct_graph(self, patched_ref_name, instance):
        patched_ref_name.return_value = "ref_2"

        ref_1 = Reference(key="ref_1", config={})
        ref_1.primary_resource = "res_1"
        ref_1.get_connections = mock.MagicMock()

        ref_2 = Reference(key="ref_2", config={})
        ref_2.primary_resource = "res_2"
        ref_2.connected_refs = {ref_1}
        ref_2.associated_resources = {"res_1"}
        ref_2.get_connections = mock.MagicMock()

        instance.references = {"ref_1": ref_1, "ref_2": ref_2}

        instance.construct_graph()

        assert instance.resources == {"res_1": ref_1, "res_2": ref_2}

        resource_1 = instance.get_node("res_1")
        resource_2 = instance.get_node("res_2")

        assert instance.nodes == {"res_1": resource_1, "res_2": resource_2}
        assert resource_1.connected_to == {resource_2: 0}

    def test_parse_paths_no_interfaces(self, instance):

        dummy_resource = Resource("res")

        instance.remove_dependent_producers = mock.MagicMock()
        instance.parse_request_parameters = mock.MagicMock()
        instance.get_associated_resource_for_ref = mock.MagicMock(return_value="res")
        instance.nodes = {"res": dummy_resource}

        instance.parse_paths([])

        instance.remove_dependent_producers.assert_called()
        instance.parse_request_parameters.assert_not_called()
        assert dummy_resource.consumers == set()
        assert dummy_resource.producers == set()
        assert dummy_resource.destructors == set()

    def test_parse_paths_with_producers(self, instance):
        dummy_resource = Resource("res")

        instance.remove_dependent_producers = mock.MagicMock()
        instance.parse_request_parameters = mock.MagicMock()
        instance.get_associated_resource_for_ref = mock.MagicMock(return_value="res")
        instance.nodes = {"res": dummy_resource}
        interface = OpenAPITaskInterface()
        interface.producer_references = "some_ref"
        interface.method = constants.POST
        interface.url = "url"

        instance.parse_paths([interface])

        instance.remove_dependent_producers.assert_called()
        instance.parse_request_parameters.assert_called()
        assert dummy_resource.consumers == set()
        assert dummy_resource.producers == {interface.op_id}
        assert dummy_resource.destructors == set()

    def test_parse_paths_with_consumers(self, instance):
        dummy_resource = Resource("res")

        def add_consumer(*args):
            ref_graph = args[1]
            ref_graph["ref"] = "consumer"

        instance.remove_dependent_producers = mock.MagicMock()
        instance.parse_request_parameters = mock.MagicMock(side_effect=add_consumer)
        instance.get_associated_resource_for_ref = mock.MagicMock(return_value="res")
        instance.nodes = {"res": dummy_resource}
        interface = OpenAPITaskInterface()
        interface.method = constants.POST
        interface.url = "url"

        instance.parse_paths([interface])

        instance.remove_dependent_producers.assert_called()
        instance.parse_request_parameters.assert_called()
        assert dummy_resource.consumers == {interface.op_id}
        assert dummy_resource.producers == set()
        assert dummy_resource.destructors == set()

    def test_parse_paths_with_destructors(self, instance):
        dummy_resource = Resource("res")

        def add_destructor(*args):
            ref_graph = args[1]
            ref_graph["ref"] = "destructor"

        instance.remove_dependent_producers = mock.MagicMock()
        instance.parse_request_parameters = mock.MagicMock(side_effect=add_destructor)
        instance.get_associated_resource_for_ref = mock.MagicMock(return_value="res")
        instance.nodes = {"res": dummy_resource}
        interface = OpenAPITaskInterface()
        interface.method = constants.POST
        interface.url = "url"

        instance.parse_paths([interface])

        instance.remove_dependent_producers.assert_called()
        instance.parse_request_parameters.assert_called()
        assert dummy_resource.consumers == {interface.op_id}
        assert dummy_resource.producers == set()
        assert dummy_resource.destructors == {interface.op_id}

    def test_parse_paths_with_no_valid_resource_node(self, instance):
        dummy_resource = Resource("res")

        def add_destructor(*args):
            ref_graph = args[1]
            ref_graph["ref"] = "destructor"

        instance.remove_dependent_producers = mock.MagicMock()
        instance.parse_request_parameters = mock.MagicMock(side_effect=add_destructor)
        instance.get_associated_resource_for_ref = mock.MagicMock(return_value="invalid_res")
        instance.nodes = {"res": dummy_resource}
        interface = OpenAPITaskInterface()
        interface.method = constants.POST
        interface.url = "url"

        instance.parse_paths([interface])

        instance.remove_dependent_producers.assert_called()
        instance.parse_request_parameters.assert_called()
        assert dummy_resource.consumers == set()
        assert dummy_resource.producers == set()
        assert dummy_resource.destructors == set()

    @mock.patch('atlas.modules.transformer.ordering.resource.utils.resolve_reference')
    def test_parse_request_parameters_with_ref(self, patched_reference, instance):

        interface = OpenAPITaskInterface()
        interface.method = constants.POST
        interface.url = "url"
        interface.parameters = {
            "param_1": {
                constants.REF: "some_ref"
            }
        }

        instance.parse_request_parameters(interface, {})

        patched_reference.assert_called()

    def test_parse_request_parameters_with_consumer_resource(self, instance):
        interface = OpenAPITaskInterface()
        interface.method = constants.POST
        interface.url = "url"
        interface.parameters = {
            "param_1": {
                constants.RESOURCE: "some_resource"
            }
        }
        instance.is_delete_resource = mock.MagicMock(return_value=False)

        ref_graph = {}
        instance.parse_request_parameters(interface, ref_graph)

        assert ref_graph == {"some_resource": "consumer"}

    def test_parse_request_parameters_with_destructor_resource(self, instance):
        interface = OpenAPITaskInterface()
        interface.method = constants.POST
        interface.url = "url"
        interface.parameters = {
            "param_1": {
                constants.RESOURCE: "some_resource"
            }
        }
        instance.is_delete_resource = mock.MagicMock(return_value=True)

        ref_graph = {}
        instance.parse_request_parameters(interface, ref_graph)

        assert ref_graph == {"some_resource": "destructor"}

    def test_parse_request_parameters_with_body_params(self, instance):
        interface = OpenAPITaskInterface()
        interface.method = constants.POST
        interface.url = "url"
        interface.parameters = {
            "param_1": {
                constants.IN_: constants.BODY_PARAM
            }
        }
        instance.get_schema_refs = mock.MagicMock(return_value=["ref_1", "ref_2"])

        ref_graph = {"ref_1": "producer", "ref_3": "producer"}
        instance.parse_request_parameters(interface, ref_graph)

        assert ref_graph == {"ref_1": "producer", "ref_2": "consumer", "ref_3": "producer"}


class TestSwaggerResourceValidator:

    @pytest.fixture
    def instance(self):
        return SwaggerResourceValidator([], {})

    def test_with_no_interfaces(self, instance):
        assert instance.get_resources_with_no_producers() == set()

    @staticmethod
    def get_resource(key):
        resource = Resource(key)
        resource.producers = {"a", "b"}
        resource.consumers = {"a", "c"}
        return resource

    @mock.patch('atlas.modules.transformer.ordering.resource.print')
    def test_functionality(self, patched_print, instance):
        inter_1 = OpenAPITaskInterface()
        inter_1.parameters = {
            # Resource, with path param, which has pure producers
            "param_1": {
                constants.RESOURCE: "resource_1",
                constants.IN_: constants.PATH_PARAM
            },
            # Resource but no path param
            "param_2": {
                constants.RESOURCE: "resource_2",
                constants.IN_: constants.BODY_PARAM
            },
            # No resource
            "param_3": {
                constants.IN_: constants.PATH_PARAM
            },
            # Resource with path param, does not have any pure producers
            "param_4": {
                constants.RESOURCE: "resource_4",
                constants.IN_: constants.PATH_PARAM
            },
        }

        instance.interfaces = [inter_1]

        res_1 = self.get_resource("resource_1")
        res_2 = self.get_resource("resource_2")
        res_3 = self.get_resource("resource_3")
        res_4 = self.get_resource("resource_4")
        res_5 = self.get_resource("resource_5")

        res_4.consumers.add("b")

        res_graph = ResourceGraph({})
        res_graph.nodes = {
            "res_1":  res_1, "res_2": res_2, "res_3": res_3, "res_4": res_4, "res_5": res_5
        }

        instance.resource_graph = res_graph

        assert instance.get_resources_with_no_producers() == {"resource_4"}

        instance.validate()
        patched_print.assert_called()
