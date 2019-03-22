from atlas.modules import constants, exceptions
from atlas.modules.transformer.ordering.base import Node, DAG
from atlas.conf import settings


class Operation(Node):
    """
    Representation for Operation Class
    """

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)


class OperationGraph(DAG):

    node_class = Operation

    def __init__(self):
        super().__init__()
        self.operations = {}

    def new_graph(self, interfaces):
        for op_interface in interfaces:
            self.add_node(op_interface.op_id)
            self.operations[op_interface.op_id] = op_interface

    def add_cartesian_edges(self, parent_keys: set, child_keys: set):
        """
        Add multiple edges in Cartesian cross-multiplication style between set of parent and child nodes
        Both sets contain keys required to add nodes

        ---- Example 1 ----
        Parent: (1, 2), child: (3, 4)
        Would generate the following edges:
        1 -> 3
        1 -> 4
        2 -> 3
        2 -> 4

        --- Example 2 -----
        Parent: (1, 2, 3), child: (3, 4)
        Here "3" is repeated in both parent and child, so it would be discarded from parent

        Rationale:
            In our case, as long as "pure" producers (i.e. parents)
            are ahead of any resource that consumes them (i.e children),
            we are looking at correct sorting

        Discarding 3 from parent, would make this example same as Example 1
        """

        parent_keys = parent_keys - child_keys

        for parent in parent_keys:
            for child in child_keys:
                self.add_edge(parent, child)

    def transform_operation(self, resource, parent_consumers, parent_producers):
        """
        Read Resource of Resource graph, and add edges in Operation Graph
        """

        resource_key = resource.get_id()

        # Read all operations which are relevant to this Resource
        node_consumers = resource.consumers
        node_producers = resource.producers
        node_destructors = resource.destructors

        # Create dummy operations if not found
        if not node_consumers:
            dummy_key = f"${resource_key}-CONSUMER"
            self.add_node(dummy_key)
            node_consumers = {dummy_key}

        if not node_producers:
            dummy_key = f"${resource_key}-PRODUCER"
            self.add_node(dummy_key)
            node_producers = {dummy_key}

        # Now, add edges for Operation Graph based on operations based on this node alone
        self.add_cartesian_edges(node_producers, node_consumers)
        self.add_cartesian_edges(node_consumers, node_destructors)

        # Second kind of edges are those which follow the same relation as those of resource graph
        self.add_cartesian_edges(parent_producers, node_producers)
        self.add_cartesian_edges(parent_consumers, node_consumers)

        return node_consumers, node_producers

    def transform_dfs(self, resource, parent_consumers, parent_producers, visited):
        """
        Recursive function to help perform DFS on resource graph
        transform_operation examines each node of Resource Graph,
            and add connections between edges of operation graph by checking the Operation relations for each resource
        """

        resource_key = resource.get_id()

        if visited[resource_key] == self.BLACK:
            return

        # Cycle Detected
        if visited[resource_key] == self.GREY:
            raise exceptions.OrderingException("Cycle Detected! Please report this to Project Maintainer")

        visited[resource_key] = self.GREY

        consumers, producers = self.transform_operation(resource, parent_consumers, parent_producers)

        for adj_resource in resource.get_connections():
            self.transform_dfs(adj_resource, consumers, producers, visited)

        visited[resource_key] = self.BLACK

    def add_custom_ordering_dependencies(self):
        """
        Add the user dependencies

        While most of the program is automated, this allows user to add their own custom ordering operations
        """

        for ordering in settings.SWAGGER_OPERATION_DEPENDENCIES:
            parent, child = ordering
            self.add_edge(parent, child)

    def transform(self, resource_graph):
        """
        Transforms Resource graph to Operation Graph.
        It relies heavily on transform_dfs function to do most of heavy lifting
        This function makes sure that:
            1. All isolated or disjoint graphs in resource graph are addressed
            2. Since we pick any arbitrary root, its ancestors are also traversed as needed
        """

        visited = {_node.get_id(): self.WHITE for _node in resource_graph}

        for node_key in resource_graph.get_vertices():
            if visited[node_key] == self.WHITE:
                self.transform_dfs(resource_graph.get_node(node_key), set(), set(), visited)
        self.add_custom_ordering_dependencies()

    def topological_sort(self):
        """
        Over-ride to do:
            1. Remove any dummy operations
            2. Make sure that delete operations are ordered at end
            3. We are returning the list of interfaces rather than Operation Names
        """

        order = super().topological_sort()

        # With the addition of Custom sorting, this logic may no longer be correct
        # Since user can explicitly order Delete Operation ahead of some other operation
        # And we ignore that
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
