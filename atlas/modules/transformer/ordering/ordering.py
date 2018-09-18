from atlas.modules import constants, utils
from atlas.modules.transformer.ordering.graph import Node, DAG
from atlas.modules.transformer.open_api_reader import SpecsFile
from atlas.modules.transformer import open_api_models


class Reference:

    def __init__(self, key, config):
        self.name = key
        self.config = config

    def is_resource(self):
        is_resource = False
        for config in self.config.get(constants.PROPERTIES, {}).values():
            resource = config.get(constants.RESOURCE)
            if resource:
                is_resource = True
                break
        return is_resource


class Resource(Node):
    """
    Representation for Resource Class
    """

    def __init__(self, key):
        super(Resource, self).__init__(key)

        self.producers = set()
        self.consumers = set()
        self.other_operations = set()

    def add_consumer(self, operation_id):
        self.consumers.add(operation_id)


class ResourceGraph(DAG):

    node_class = Resource

    def __init__(self, references: dict):
        super(ResourceGraph, self).__init__()
        self.resources = dict()
        self.references = [Reference(key, config) for key, config in references.items()]

    def construct_graph(self):

        # Add all nodes first
        for reference in self.references:
            self.resources[reference.name] = reference.config
            self.add_node(reference.name)

        # Now add edges between the nodes
        for resource_key, resource_config in self.resources.items():
            for config in resource_config.get(constants.PROPERTIES, {}).values():
                _type = config.get(constants.TYPE)
                if _type == constants.ARRAY:
                    config = config.get(constants.ITEMS, {})
                ref = config.get(constants.REF)
                if ref:
                    source_key = utils.get_ref_name(ref)
                    self.add_edge(source_key, resource_key)

    def parse_paths(self, interfaces):

        for operation in interfaces:
            op_id = operation.func_name
            for parameter in operation.parameters.values():
                in_ = parameter[constants.IN_]
                if in_ == constants.BODY_PARAM:
                    ref = parameter.get(constants.SCHEMA, {}).get(constants.REF)
                    if ref:
                        ref_name = utils.get_ref_name(ref)
                        resource = self.nodes.get(ref_name)
                        if resource:
                            resource.add_consumer(op_id)


class Operation(Node):
    """
    Representation for Operation Class
    """


class OperationGraph(DAG):

    def new_graph(self, paths):
        for config in paths.values():
            for method_config in config.values():
                self.add_node(method_config.get(constants.OPERATION))

    def transform_dfs(self, resource_key, parent_consumers, visited, resource_graph: ResourceGraph):
        """
        Transform Reference Graph to Operation Graph.
        Takes a resource key and perform a DFS Operation taking that node as root node.
        """

        resource = resource_graph.get_node(resource_key)

        node_consumers = resource.consumers

        if not node_consumers:
            print(resource_key)
            dummy_key = "${}".format(resource_key)
            self.add_node(dummy_key)
            node_consumers = {dummy_key}

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
            self.transform_dfs(adj_resource.get_id(), node_consumers, visited, resource_graph)

        visited[resource_key] = self.BLACK

    def transform(self, resource_graph: ResourceGraph):
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
                self.transform_dfs(node, set(), visited, resource_graph)


if __name__ == "__main__":
    specs = SpecsFile().file_load()

    open_api = open_api_models.OpenAPISpec(specs)
    open_api.get_interfaces()

    resource_definitions = specs.get(constants.DEFINITIONS)
    res_graph = ResourceGraph(resource_definitions)
    res_graph.construct_graph()
    res_graph.parse_paths(open_api.interfaces)

    res_graph.top_sort()

    op_graph = OperationGraph()
    op_graph.new_graph(specs.get(constants.PATHS))
    op_graph.transform(res_graph)

    # print(res_graph.top_sort())
    print(op_graph.top_sort())
