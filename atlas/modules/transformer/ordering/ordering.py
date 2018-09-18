from atlas.modules import constants
from atlas.modules.transformer.open_api_reader import SpecsFile
from atlas.modules.transformer import open_api_models
from atlas.modules.transformer.ordering import resource, operation


class Ordering:

    def __init__(self):
        self.specs = SpecsFile().file_load()
        self.open_api = open_api_models.OpenAPISpec(self.specs)
        self.open_api.get_interfaces()

    def get_resource_graph(self):
        resource_definitions = self.specs.get(constants.DEFINITIONS)
        res_graph = resource.ResourceGraph(resource_definitions)
        res_graph.construct_graph()
        res_graph.parse_paths(self.open_api.interfaces)
        return res_graph

    def construct_order_graph(self, res_graph):
        op_graph = operation.OperationGraph()
        op_graph.new_graph(self.specs.get(constants.PATHS))
        op_graph.transform(res_graph)
        return op_graph

    def order(self):
        res_graph = self.get_resource_graph()
        op_graph = self.construct_order_graph(res_graph)
        return op_graph.top_sort()
