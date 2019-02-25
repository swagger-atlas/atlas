from collections import deque

from atlas.modules import exceptions


class Node:

    def __init__(self, key):
        self.key = key
        self.connected_to = {}

    def add_neighbour(self, nbr, weight=0):
        self.connected_to[nbr] = weight

    def get_connections(self):
        return self.connected_to.keys()

    def get_id(self):
        return self.key

    def get_weight(self, nbr):
        return self.connected_to[nbr]

    def __str__(self):
        return str(self.key) + ' connected to: ' + str([node.get_id() for node in self.connected_to])


class DirectedGraph:

    node_class = Node

    def __init__(self):
        self.nodes = {}
        self.node_count = 0

    def add_node(self, key):
        node = self.nodes.get(key)

        if not node:
            self.node_count = self.node_count + 1
            node = self.node_class(key)
            self.nodes[key] = node

        return node

    def get_node(self, node_key):
        return self.nodes.get(node_key)

    def add_edge(self, node_1_key, node_2_key, weight=0):
        node_1 = self.nodes.get(node_1_key, self.add_node(node_1_key))
        node_2 = self.nodes.get(node_2_key, self.add_node(node_2_key))
        self.add_edge_by_node(node_1, node_2, weight)

    def add_edge_by_node(self, node_1, node_2, weight=0):
        node_1.add_neighbour(node_2, weight)

    def get_vertices(self):
        return self.nodes.keys()

    def dfs(self, node: Node, visited=None, order=None):
        # Depth first search

        if visited is None:
            visited = set()
            order = []

        visited.add(node)
        order.append(node)

        for neighbour in set(node.get_connections()) - visited:
            self.dfs(neighbour, visited, order)

        return order

    def __iter__(self):
        return iter(self.nodes.values())

    def __contains__(self, key):
        return key in self.nodes


class DAG(DirectedGraph):
    """
    Directed Acyclic Graph.
    """

    WHITE = 1
    GREY = 2
    BLACK = 3

    def add_edge_by_node(self, node_1, node_2, weight=0):
        # Avoid easy self-referential node cycles
        if node_1 != node_2:
            super().add_edge_by_node(node_1, node_2, weight)

    def sort_helper(self, node_key, visited, order):

        if visited[node_key] == self.BLACK:
            return

        if visited[node_key] == self.GREY:
            raise exceptions.OrderingException("Cycle detected in the graph. Please report it to Project Maintainer")

        visited[node_key] = self.GREY

        for neighbour in self.get_node(node_key).get_connections():
            self.sort_helper(neighbour.get_id(), visited, order)

        visited[node_key] = self.BLACK
        order.appendleft(node_key)

    def topological_sort(self):
        """
        Topologically sort the graph
        https://en.wikipedia.org/wiki/Topological_sorting
        We are using DFS method
        """

        visited = {_node.get_id(): self.WHITE for _node in self}
        order = deque()

        for node in self.get_vertices():
            if visited[node] == self.WHITE:
                self.sort_helper(node, visited, order)

        return order
