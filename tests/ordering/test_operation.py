from unittest import mock

import pytest

from atlas.modules.transformer.ordering.operation import OperationGraph, Operation, constants, exceptions
from atlas.modules.transformer.ordering.resource import Resource
from atlas.modules.transformer.interface import OpenAPITaskInterface


class TestOperation:

    @pytest.fixture
    def instance(self):
        return OperationGraph()

    @staticmethod
    def create_interface(method=None, url=None):
        interface = OpenAPITaskInterface()
        interface.method = method or constants.GET
        interface.url = url or "url"
        return interface

    def test_new_graph_no_interfaces(self, instance):
        instance.new_graph([])
        assert instance.operations == {}
        assert instance.nodes == {}

    def test_new_graph_with_interfaces(self, instance):
        interface = self.create_interface()

        instance.new_graph([interface])

        assert instance.operations == {interface.op_id: interface}
        assert instance.nodes == {interface.op_id: Operation(interface.op_id)}

    @mock.patch('atlas.modules.transformer.ordering.operation.OperationGraph.add_edge')
    def test_add_cartesian_edges(self, add_edge_patch, instance):
        instance.add_cartesian_edges({1, 2, 3, 4}, {1, 3, 5, 7})

        assert add_edge_patch.call_args_list == [
            ((2, 1),), ((2, 3),), ((2, 5),), ((2, 7),), ((4, 1),), ((4, 3),), ((4, 5),), ((4, 7),)
        ]

    @mock.patch('atlas.modules.transformer.ordering.operation.settings')
    @mock.patch('atlas.modules.transformer.ordering.operation.OperationGraph.add_edge')
    def test_add_custom_ordering_dependencies(self, add_edge_patch, patched_settings, instance):
        patched_settings.SWAGGER_OPERATION_DEPENDENCIES = [(1, 2), (2, 3)]

        instance.add_custom_ordering_dependencies()

        assert add_edge_patch.call_args_list == [
            ((1, 2),), ((2, 3),)
        ]

    def test_topological_sort(self, instance):
        interface_1 = self.create_interface(url="url_1")
        interface_2 = self.create_interface(url="url_2")
        interface_3 = self.create_interface(url="url_3", method=constants.DELETE)
        interface_4 = self.create_interface(url="url_4", method=constants.DELETE)

        instance.new_graph([interface_1, interface_2, interface_3, interface_4])

        instance.add_edge(interface_1.op_id, interface_2.op_id)
        instance.add_edge(interface_1.op_id, interface_3.op_id)
        instance.add_edge(interface_4.op_id, interface_2.op_id)
        instance.add_edge(interface_4.op_id, interface_3.op_id)

        # Normal Topological sort would be (1, 4) --> (3, 2)
        # Since delete operations are shuffled back, we get(1-2- (3, 4))
        assert instance.topological_sort() == [interface_1, interface_2, interface_4, interface_3]

    @mock.patch('atlas.modules.transformer.ordering.operation.OperationGraph.add_cartesian_edges')
    def test_transform_operation(self, patched_add_cartesian_edge, instance):
        res_instance = Resource("resource")
        res_instance.producers = {"p_1", "p_2"}
        res_instance.consumers = {"c_1", "c_2"}
        res_instance.destructors = {"d_1", "d_2"}

        assert instance.transform_operation(res_instance, {"pc_1", "pc_2"}, {"pp_1", "pp_2"}) == (
            {"c_1", "c_2"}, {"p_1", "p_2"}
        )

        assert patched_add_cartesian_edge.call_args_list == [
            (({"p_1", "p_2"}, {"c_1", "c_2"}),),
            (({"c_1", "c_2"}, {"d_1", "d_2"}),),
            (({"pp_1", "pp_2"}, {"p_1", "p_2"}),),
            (({"pc_1", "pc_2"}, {"c_1", "c_2"}),),
        ]

    @mock.patch('atlas.modules.transformer.ordering.operation.OperationGraph.add_cartesian_edges')
    def test_transform_operation_with_no_consumer_producers(self, patched_add_cartesian_edge, instance):
        res_instance = Resource("resource")

        assert instance.transform_operation(res_instance, {"pc_1", "pc_2"}, {"pp_1", "pp_2"}) == (
            {"$resource-CONSUMER"}, {"$resource-PRODUCER"}
        )

        assert patched_add_cartesian_edge.call_args_list == [
            (({"$resource-PRODUCER"}, {"$resource-CONSUMER"}),),
            (({"$resource-CONSUMER"}, set()),),
            (({"pp_1", "pp_2"}, {"$resource-PRODUCER"}),),
            (({"pc_1", "pc_2"}, {"$resource-CONSUMER"}),),
        ]

    def test_transform_dfs_cycle(self, instance):
        res_instance = Resource("resource")
        visited = {res_instance.get_id(): instance.GREY}

        with pytest.raises(exceptions.OrderingException):
            instance.transform_dfs(res_instance, set(), set(), visited)

    @mock.patch('atlas.modules.transformer.ordering.operation.OperationGraph.transform_operation')
    def test_transform_dfs_existing_node(self, patched_transform_op, instance):
        res_instance = Resource("resource")
        visited = {res_instance.get_id(): instance.BLACK}

        instance.transform_dfs(res_instance, set(), set(), visited)

        assert patched_transform_op.assert_not_called
