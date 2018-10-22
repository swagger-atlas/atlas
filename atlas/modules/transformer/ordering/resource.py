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

    def __init__(self, references: dict, specs=None):
        super(ResourceGraph, self).__init__()
        self.resources = dict()
        self.references = [Reference(key.lower(), config) for key, config in references.items()]
        self.specs = specs or {}

    @staticmethod
    def convert_ref_name_to_resource(ref_name: str) -> str:
        return "".join([x.lower() for x in re.sub("-", "_", ref_name).split("_")])

    def add_ref_edge(self, ref, dependent_key):
        if ref:
            source_key = utils.get_ref_name(ref)
            source_resource = self.convert_ref_name_to_resource(source_key)
            # Note the edge - Source is required for resource
            self.add_edge(source_resource, dependent_key)

    @staticmethod
    def process_resource_for_refs(resource_config: dict) -> (set, set):
        """
        Process a single resource and return set of all references from it
        """
        refs = set()
        resources = set()

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
            resource = config.get(constants.RESOURCE)
            resources.add(resource)

        # Now look through Additional properties to see if there is any ref there
        additional_properties = resource_config.get(constants.ADDITIONAL_PROPERTIES, {})

        if additional_properties and isinstance(additional_properties, dict):
            refs.add(additional_properties.get(constants.REF))
            resources.add(additional_properties.get(constants.RESOURCE))

        return refs, resources

    def construct_graph(self):

        # Add all nodes first
        for reference in self.references:
            resource_name = self.convert_ref_name_to_resource(reference.name)
            self.resources[resource_name] = reference.config
            self.add_node(resource_name)

        # Now add edges between the nodes
        for resource_key, resource_config in self.resources.items():
            refs, resources = self.process_resource_for_refs(resource_config)
            for ref in refs:
                self.add_ref_edge(ref, resource_key)
            for resource in resources:
                if resource:
                    self.add_edge(resource, resource_key)

    @staticmethod
    def get_ref_name(config):
        schema = config.get(constants.SCHEMA, {})

        # Search in simple direct ref or array ref
        ref = schema.get(constants.REF)

        if schema and not ref:
            items = schema.get(constants.ITEMS, {})
            if items and isinstance(items, dict):
                ref = items.get(constants.REF)

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

                parameter_ref = parameter.get(constants.REF)
                if parameter_ref:
                    parameter = utils.resolve_reference(self.specs, parameter_ref)

                resource = parameter.get(constants.RESOURCE)
                if resource:
                    # This time, it is Path Params, so we are sure that is is consumer
                    ref_graph[resource] = "consumer"

                ref = self.get_ref_name(parameter)
                # If it is already claimed as producer/consumer, then respect that
                if ref and ref not in ref_graph:
                    ref_graph[ref] = "consumer"

            for ref, ref_op in ref_graph.items():
                resource_node = self.nodes.get(self.convert_ref_name_to_resource(ref))
                ref_op = "add_consumer" if ref_op == "consumer" else "add_producer"
                if resource_node:
                    getattr(resource_node, ref_op)(op_id)
