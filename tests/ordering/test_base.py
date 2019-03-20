import pytest

from atlas.modules.transformer.ordering.base import Node, DAG, DirectedGraph, exceptions


class TestNode:

    @pytest.fixture
    def instance(self):
        return Node(key="key")

    def test_add_neighbour(self, instance):
        instance.add_neighbour("node")
        assert instance.connected_to == {"node": 0}

    def test_get_connections(self, instance):
        instance.connected_to = {"a": 1, "b": 0}
        assert set(instance.get_connections()) == {"a", "b"}

    def test_get_id(self, instance):
        assert instance.get_id() == "key"

    def test_get_weight(self, instance):
        instance.connected_to = {"a": 1, "b": 0}
        assert instance.get_weight("a") == 1

    def test_str(self, instance):
        node_neighbour = Node("abc")
        instance.connected_to = {node_neighbour: 1}

        assert str(instance) == "key connected to: ['abc']"


class TestDirectedGraph:

    @pytest.fixture
    def instance(self):
        return DirectedGraph()

    def test_add_node_new_node(self, instance):
        instance.nodes = {}
        instance.node_count = 0

        ret = instance.add_node("key")

        assert instance.node_count == 1
        assert instance.nodes == {"key": ret}

    def test_add_node_existing_node(self, instance):
        sample = Node("sample")
        instance.nodes = {"key": sample}
        instance.node_count = 1

        assert instance.add_node("key") == sample

        assert instance.node_count == 1
        assert instance.nodes == {"key": sample}

    def test_get_node(self, instance):
        sample = Node("sample")
        instance.nodes = {"key": sample}
        assert instance.get_node("key") == sample

    def test_add_edge(self, instance):
        node_1 = Node("node_1")
        node_2 = Node("node_2")
        instance.nodes = {"node_1": node_1, "node_2": node_2}

        instance.add_edge("node_1", "node_2", 2)

        assert node_1.connected_to == {node_2: 2}

    def test_get_vertices(self, instance):
        node_1 = Node("node_1")
        node_2 = Node("node_2")
        instance.nodes = {"node_1": node_1, "node_2": node_2}

        assert set(instance.get_vertices()) == {"node_1", "node_2"}

    def test_iter(self, instance):
        node_1 = Node("node_1")
        node_2 = Node("node_2")
        instance.nodes = {"node_1": node_1, "node_2": node_2}

        assert {node for node in instance} == {node_1, node_2}

    def test_contains(self, instance):
        node_1 = Node("node_1")
        node_2 = Node("node_2")
        instance.nodes = {"node_1": node_1, "node_2": node_2}

        assert "node_1" in instance
        assert "node_3" not in instance

    def test_dfs(self, instance):
        node_1 = Node("node_1")
        node_2 = Node("node_2")
        instance.nodes = {"node_1": node_1, "node_2": node_2}
        instance.add_edge_by_node(node_1, node_2)

        assert instance.dfs(node_1) == [node_1, node_2]
        assert instance.dfs(node_2) == [node_2]


class TestDAG:

    @pytest.fixture
    def instance(self):
        instance = DAG()
        node_1 = Node("node_1")
        node_2 = Node("node_2")
        node_3 = Node("node_3")
        instance.nodes = {"node_1": node_1, "node_2": node_2, "node_3": node_3}
        instance.add_edge_by_node(node_1, node_2)
        instance.add_edge_by_node(node_3, node_1)
        return instance

    def test_topological_sort(self, instance):
        assert list(instance.topological_sort()) == ["node_3", "node_1", "node_2"]

    def test_add_self_referential_edge(self, instance):
        """
        DAG Should not add self-referential edge
        """
        instance.add_edge("node_1", "node_1")

        node_1 = instance.get_node("node_1")
        node_2 = instance.get_node("node_2")

        assert node_1.connected_to == {node_2: 0}

    def test_topological_sort_with_cycle(self, instance):
        node_1 = instance.get_node("node_1")
        node_2 = instance.get_node("node_2")
        instance.add_edge_by_node(node_2, node_1)

        with pytest.raises(exceptions.OrderingException):
            instance.topological_sort()
