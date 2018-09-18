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
