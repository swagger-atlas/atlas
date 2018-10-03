import re

from atlas.modules import constants, utils
from atlas.modules.transformer.ordering.base import Node, DAG


class Reference:

    def __init__(self, key, config):
        self.name = key
        self.config = config


class Resource(Node):
    """
    Representation for Resource Class
    """

    def __init__(self, key):
        super(Resource, self).__init__(key)

        self.producers = set()
        self.consumers = set()
        self.other_operations = set()

    def add_consumer(self, operation_id: str):
        self.consumers.add(operation_id)

    def add_producer(self, operation_id: str):
        self.producers.add(operation_id)


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
                    # Note the edge - Source is required for resource
                    self.add_edge(source_key, resource_key)

    @staticmethod
    def get_ref_name(config):
        schema = config.get(constants.SCHEMA, {})

        # Search in simple direct ref or array ref
        ref = schema.get(constants.REF) or schema.get(constants.ITEMS, {}).get(constants.REF)
        return utils.get_ref_name(ref) if ref else None

    def parse_paths(self, interfaces):

        for operation in interfaces:
            op_id = operation.func_name
            ref_graph = {}
            for response in operation.responses.values():
                ref = self.get_ref_name(response)
                if ref:
                    ref_graph[ref] = "producer"
            for parameter in operation.parameters.values():
                ref = self.get_ref_name(parameter)
                # If it is already claimed as producer, then respect that
                if ref and ref not in ref_graph:
                    ref_graph[ref] = "consumer"

                # Try to find if it is Path Params Resource
                # This should over-write any previous value
                if not ref:
                    resource = parameter.get(constants.RESOURCE)
                    if resource:
                        # This time, it is Path Params, so we are sure that is is consumer
                        ref_graph[resource] = "consumer"

            for ref, ref_op in ref_graph.items():
                ref_node = self.nodes.get(ref)
                ref_op = "add_consumer" if ref_op == "consumer" else "add_producer"
                if ref_node:
                    getattr(ref_node, ref_op)(op_id)
