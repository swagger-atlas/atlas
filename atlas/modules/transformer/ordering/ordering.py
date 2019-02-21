from atlas.modules import constants
from atlas.modules.helpers.open_api_reader import SpecsFile
from atlas.modules.transformer import open_api_models
from atlas.modules.transformer.ordering import resource, operation


class Ordering:
    """
    This is responsible for ordering APIs in a correct format
    Entry Point: order()

    See references/ordering.md for detailed concept on same
    """

    def __init__(self, specs=None, interfaces=None):
        self.specs = specs or SpecsFile().file_load()

        if not interfaces:
            open_api = open_api_models.OpenAPISpec(self.specs)
            open_api.get_interfaces()
            interfaces = open_api.interfaces

        self.interfaces = interfaces

    def get_resource_graph(self):
        resource_definitions = self.specs.get(constants.DEFINITIONS)
        res_graph = resource.ResourceGraph(resource_definitions, self.specs)
        res_graph.construct_graph()
        res_graph.parse_paths(self.interfaces)
        return res_graph

    def construct_order_graph(self, res_graph):
        op_graph = operation.OperationGraph()
        op_graph.new_graph(self.interfaces)
        op_graph.transform(res_graph)
        return op_graph

    def order(self):
        """
        Please see references/ordering.md for details about data structures and general concepts

        Ordering APIs/operation consists of several steps:
            - Construction of reference Objects, which is then used to construct resource graph
            - Validating resource graph
            - Using resource graph to construct Operation Graph
            - Topologically sorting operation graph to get the required order
        """
        res_graph = self.get_resource_graph()
        validator = resource.SwaggerResourceValidator(res_graph, self.interfaces)
        validator.validate()
        op_graph = self.construct_order_graph(res_graph)
        return op_graph.topological_sort()
