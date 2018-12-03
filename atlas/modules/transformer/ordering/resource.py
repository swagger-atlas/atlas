from atlas.modules import constants, exceptions, utils
from atlas.modules.helpers import open_api
from atlas.modules.transformer.ordering.base import Node, DAG


class Reference:

    def __init__(self, key, config):
        self.name = key
        self.config = config

        self.connected_refs = set()
        self.connected_resources = set()

        self.primary_resource = None

    def add_connected_ref(self, value):
        if value:
            self.connected_refs.add(value)

    def add_connected_resource(self, value):
        if value:
            self.connected_resources.add(value)

    def resolve_primary_resource(self, candidates: set):
        candidates = candidates or self.connected_resources

        # Only one candidate is there, so we have clear primary resource
        if len(candidates) == 1:
            self.primary_resource = self.connected_resources.pop()
        elif not candidates:
            # There are no candidates, so just name resource after reference
            self.primary_resource = self.name
        else:
            # We cannot determine the best candidate
            raise exceptions.ResourcesException(f"Could not determine primary resource for {self.name}")

    def get_connections(self):

        primary_resource_fields = set()

        # Look through properties
        for name, config in self.config.get(constants.PROPERTIES, {}).items():
            field = open_api.ReferenceField(name, config)
            self.add_connected_ref(field.ref)
            self.add_connected_resource(field.resource)

            if field.can_contain_primary_resource:
                primary_resource_fields.add(field.resource)

        # Now look through Additional properties to see if there is any ref there
        additional_properties = self.config.get(constants.ADDITIONAL_PROPERTIES, {})

        if additional_properties and isinstance(additional_properties, dict):
            self.add_connected_ref(additional_properties.get(constants.REF))
            self.add_connected_resource(additional_properties.get(constants.RESOURCE))

        self.resolve_primary_resource(primary_resource_fields)


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
        self.references = {key.lower(): Reference(key.lower(), config) for key, config in references.items()}
        # self.references = [Reference(key.lower(), config) for key, config in references.items()]
        self.specs = specs or {}

    def get_associated_resource_for_ref(self, ref_name: str) -> str:
        return self.references[ref_name.lower()].primary_resource

    def add_ref_edge(self, ref, dependent_key):
        """
        Add resource edge by extracting resource from ref
        """
        if ref:
            source_key = utils.get_ref_name(ref)
            source_resource = self.get_associated_resource_for_ref(source_key)
            # Note the edge - Source is required for resource
            self.add_edge(source_resource, dependent_key)

    def construct_graph(self):

        # Add all nodes first
        for ref_name, reference in self.references.items():
            reference.get_connections()
            resource_name = self.get_associated_resource_for_ref(ref_name)
            self.resources[resource_name] = reference
            self.add_node(resource_name)

        # Now add edges between the nodes
        for resource_key, reference in self.resources.items():
            for ref in reference.connected_refs:
                self.add_ref_edge(ref, resource_key)
            for resource in reference.connected_resources:
                if resource:
                    self.add_edge(resource, resource_key)

    @staticmethod
    def get_schema_refs(config):
        schema = open_api.Schema(config.get(constants.SCHEMA, {}))
        return [utils.get_ref_name(ref).lower() for ref in schema.get_all_refs()]

    def parse_paths(self, interfaces):

        for operation in interfaces:
            op_id = operation.func_name
            ref_graph = {}
            self.parse_responses(operation, ref_graph)
            self.parse_request_parameters(operation, ref_graph)

            for ref, ref_op in ref_graph.items():
                resource_node = self.nodes.get(self.get_associated_resource_for_ref(ref))
                ref_op = "add_consumer" if ref_op == "consumer" else "add_producer"
                if resource_node:
                    getattr(resource_node, ref_op)(op_id)

    def parse_responses(self, operation, ref_graph):
        """
        Parse Responses for a single operation and mark References w.r.t to Operation
        """

        for response in operation.responses.values():
            if operation.method in {constants.DELETE, constants.PATCH, constants.PUT}:
                continue
            response_refs = self.get_schema_refs(response)
            for ref in response_refs:
                ref_graph[ref] = "producer"

    def parse_request_parameters(self, operation, ref_graph):
        """
        Parse Request Parameters for a single operation and mark References w.r.t to Operation
        """

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

            if parameter.get(constants.TYPE) == constants.BODY_PARAM:
                request_refs = self.get_schema_refs(parameter)

                # If it is already claimed as producer/consumer, then respect that
                for ref in request_refs:
                    if ref not in ref_graph:
                        ref_graph[ref] = "consumer"
