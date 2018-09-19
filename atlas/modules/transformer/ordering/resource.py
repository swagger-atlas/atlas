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
        # If operation is both consuming and producing the same resource
        # Assume that it is its producer, and not consumer
        if operation_id not in self.producers:
            self.consumers.add(operation_id)

    def add_producer(self, operation_id: str):
        # If operation is both consuming and producing the same resource
        # Assume that it is its producer, and not consumer
        if operation_id in self.consumers:
            self.consumers.remove(operation_id)
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

    def update_resource_operation(self, config, update_func, operation_id):
        schema = config.get(constants.SCHEMA, {})

        # Search in simple direct ref or array ref
        ref = schema.get(constants.REF) or schema.get(constants.ITEMS, {}).get(constants.REF)
        ref_name = ""

        if ref:
            ref_name = utils.get_ref_name(ref)
        else:
            # Try to see if it it has any resource that can match ref
            resource = config.get(constants.RESOURCE)
            if resource:
                # Convert it to CamelCase for matching purposes
                snake_case = re.sub("-", "_", resource)
                ref_name = "".join([x.title() for x in snake_case.split("_")])

        if ref_name:
            ref_node = self.nodes.get(ref_name)
            if ref_node:
                getattr(ref_node, update_func)(operation_id)

    def parse_paths(self, interfaces):

        for operation in interfaces:
            op_id = operation.func_name
            for parameter in operation.parameters.values():
                self.update_resource_operation(parameter, "add_consumer", op_id)
            for response in operation.responses.values():
                self.update_resource_operation(response, "add_producer", op_id)
