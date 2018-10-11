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
        self.references = [Reference(key.lower(), config) for key, config in references.items()]

    def add_ref_edge(self, ref, dependent_key):
        if ref:
            source_key = utils.get_ref_name(ref)
            # Note the edge - Source is required for resource
            self.add_edge(source_key, dependent_key)

    @staticmethod
    def process_resource_for_refs(resource_config: dict) -> set:
        """
        Process a single resource and return set of all references from it
        """
        refs = set()

        # ########## --  Ignore ALL OF, since adding these relations gave us several cycles -- ####

        # # Check if there is reference
        # # This is needed when this is called recursively via All of mechanism
        # refs.add(resource_config.get(constants.REF))

        # # Recursively process ALL OF sub-schemas
        # for schema in resource_config.get(constants.ALL_OF, []):
        #     refs.update(self.process_resource_for_refs(schema))

        # ####### -- Rest of code starts here ------- ###################

        # Look through properties
        for config in resource_config.get(constants.PROPERTIES, {}).values():
            _type = config.get(constants.TYPE)
            if _type == constants.ARRAY:
                config = config.get(constants.ITEMS, {})
            ref = config.get(constants.REF)
            refs.add(ref)

        # Now look through Additional properties to see if there is any ref there
        refs.add(resource_config.get(constants.ADDITIONAL_PROPERTIES, {}).get(constants.REF))

        return refs

    def construct_graph(self):

        # Add all nodes first
        for reference in self.references:
            self.resources[reference.name] = reference.config
            self.add_node(reference.name)

        # Now add edges between the nodes
        for resource_key, resource_config in self.resources.items():
            refs = self.process_resource_for_refs(resource_config)
            for ref in refs:
                self.add_ref_edge(ref, resource_key)

    @staticmethod
    def get_ref_name(config):
        schema = config.get(constants.SCHEMA, {})

        # Search in simple direct ref or array ref
        ref = schema.get(constants.REF) or schema.get(constants.ITEMS, {}).get(constants.REF)
        return utils.get_ref_name(ref).lower() if ref else None

    def parse_paths(self, interfaces):

        for operation in interfaces:
            op_id = operation.func_name
            ref_graph = {}
            for response in operation.responses.values():
                ref = self.get_ref_name(response)
                if ref:
                    ref_graph[ref] = "producer"
            for parameter in operation.parameters.values():
                # Try to find if it is Path Params Resource
                # This should over-write any previous value
                resource = parameter.get(constants.RESOURCE)
                if resource:
                    # This time, it is Path Params, so we are sure that is is consumer
                    ref_graph[resource] = "consumer"

                ref = self.get_ref_name(parameter)
                # If it is already claimed as producer/consumer, then respect that
                if ref and ref not in ref_graph:
                    ref_graph[ref] = "consumer"

            for ref, ref_op in ref_graph.items():
                ref_node = self.nodes.get(ref)
                ref_op = "add_consumer" if ref_op == "consumer" else "add_producer"
                if ref_node:
                    getattr(ref_node, ref_op)(op_id)
