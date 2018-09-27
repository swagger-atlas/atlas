from atlas.modules import constants, exceptions
from atlas.modules.transformer.ordering.base import Node, DAG


class Operation(Node):
    """
    Representation for Operation Class
    """


class OperationGraph(DAG):

    def __init__(self):
        super().__init__()
        self.operations = {}

    def new_graph(self, interfaces):
        for op_interface in interfaces:
            self.add_node(op_interface.func_name)
            self.operations[op_interface.func_name] = op_interface

    def add_cartesian_edges(self, parent_keys: set, child_keys: set):
        """
        Add multiple edges in Cartesian cross-multiplication style between set of parent and child nodes
        Both sets contain keys required to add nodes
        """

        for parent in parent_keys:
            for child in child_keys:
                self.add_edge(parent, child)

    def transform_dfs(self, resource_key, parent_consumers, parent_producers, visited, resource_graph):
        """
        Transform Reference Graph to Operation Graph.
        Takes a resource key and perform a DFS Operation taking that node as root node.
        """

        resource = resource_graph.get_node(resource_key)

        node_consumers = resource.consumers
        node_producers = resource.producers

        if not node_consumers:
            dummy_key = "${}-CONSUMER".format(resource_key)
            self.add_node(dummy_key)
            node_consumers = {dummy_key}

        if not node_producers:
            dummy_key = "${}-PRODUCER".format(resource_key)
            self.add_node(dummy_key)
            node_producers = {dummy_key}

        self.add_cartesian_edges(node_producers, node_consumers)
        self.add_cartesian_edges(parent_producers, node_producers)
        self.add_cartesian_edges(parent_consumers, node_consumers)

        if visited[resource_key] == self.BLACK:
            return

        # Cycle Detected
        if visited[resource_key] == self.GREY:
            raise exceptions.OrderingException("Cycle Detected! Please report this to Project Maintainer")

        visited[resource_key] = self.GREY

        for adj_resource in resource.get_connections():
            self.transform_dfs(adj_resource.get_id(), node_consumers, node_producers, visited, resource_graph)

        visited[resource_key] = self.BLACK

    def transform(self, resource_graph):
        """
        Transforms Resource graph to Operation Graph.
        It relies heavily on transform_dfs function to do most of heavy lifting
        This function makes sure that:
            1. All isolated or disjoint graphs in resource graph are addressed
            2. Since we pick any arbitrary root, its ancestors are also traversed as needed
        """

        visited = {_node.get_id(): self.WHITE for _node in resource_graph}

        for node in resource_graph.get_vertices():
            if visited[node] == self.WHITE:
                self.transform_dfs(node, set(), set(), visited, resource_graph)

    def topological_sort(self):
        """
        Over-ride to do:
            1. Remove any dummy operations
            2. Make sure that delete operations are ordered at end
            3. We are returning the list of interfaces rather than Operation Names
        """

        order = super().topological_sort()

        interface_order = []
        delete_order = []

        for op_name in order:
            interface = self.operations.get(op_name)
            if interface:
                if interface.method == constants.DELETE:
                    delete_order.append(interface)
                else:
                    interface_order.append(interface)

        return interface_order + delete_order
