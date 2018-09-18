from atlas.modules import constants
from atlas.modules.transformer.ordering.base import Node, DAG


class Operation(Node):
    """
    Representation for Operation Class
    """


class OperationGraph(DAG):

    def new_graph(self, paths):
        for config in paths.values():
            for method_config in config.values():
                self.add_node(method_config.get(constants.OPERATION))

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

        for producer in node_producers:
            for consumer in node_consumers:
                op_node_1 = self.get_node(producer)
                op_node_2 = self.get_node(consumer)
                self.add_edge_by_node(op_node_1, op_node_2)

        for producer in node_producers:
            for parent_producer in parent_producers:
                op_node_1 = self.get_node(parent_producer)
                op_node_2 = self.get_node(producer)
                self.add_edge_by_node(op_node_1, op_node_2)

        for consumer in node_consumers:
            for parent_consumer in parent_consumers:
                op_node_1 = self.get_node(parent_consumer)
                op_node_2 = self.get_node(consumer)
                self.add_edge_by_node(op_node_1, op_node_2)

        if visited[resource_key] == self.BLACK:
            return

        # Cycle Detected
        if visited[resource_key] == self.GREY:
            raise Exception("Cycle Detected")

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
