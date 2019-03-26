from atlas.modules import constants, exceptions, utils
from atlas.modules.helpers import open_api
from atlas.modules.transformer.ordering.base import Node, DAG


class Reference:
    """
    Reference Class.
    Contains information about Swagger Definition connections
    """

    def __init__(self, key, config):
        self.name = key
        self.config = config

        # Other definitions this reference points to
        self.connected_refs = set()

        # Resources which are available for this definition
        self.associated_resources = set()
        self.primary_resource = None

    def add_connected_ref(self, value):
        if value:
            self.connected_refs.add(value)

    def add_resource_association(self, value):
        if value:
            self.associated_resources.add(value)

    def resolve_primary_resource(self, candidates: set):
        candidates = candidates or self.associated_resources

        # Only one candidate is there, so we have clear primary resource
        if len(candidates) == 1:
            self.primary_resource = candidates.pop()
            self.associated_resources.discard(self.primary_resource)
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
            self.add_resource_association(field.resource)

            if field.can_contain_primary_resource:
                primary_resource_fields.add(field.resource)

        # Now look through Additional properties to see if there is any ref there
        additional_properties = self.config.get(constants.ADDITIONAL_PROPERTIES, {})

        if additional_properties and isinstance(additional_properties, dict):
            self.add_connected_ref(additional_properties.get(constants.REF))
            self.add_resource_association(additional_properties.get(constants.RESOURCE))

        self.resolve_primary_resource(primary_resource_fields)


class Resource(Node):
    """
    Representation for Resource Class
    """

    def __init__(self, key):
        super(Resource, self).__init__(key)

        self.producers = set()
        self.consumers = set()
        self.destructors = set()

    def add_consumer(self, operation_id: str):
        self.consumers.add(operation_id)

    def add_producer(self, operation_id: str):
        self.producers.add(operation_id)

    def add_destructor(self, operation_id: str):
        # If some op is destroying resource, it must also consume them
        self.destructors.add(operation_id)
        self.consumers.add(operation_id)


class ResourceGraph(DAG):

    node_class = Resource

    def __init__(self, references: dict, specs: dict = None):
        super(ResourceGraph, self).__init__()
        self.resources = dict()
        self.references = {key.lower(): Reference(key.lower(), config) for key, config in references.items()}
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
            # Note the direction of edge - Source is required for resource
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
            for resource in reference.associated_resources:
                self.add_edge(resource, resource_key)

    @staticmethod
    def get_schema_refs(config):
        schema = open_api.Schema(config.get(constants.SCHEMA, {}))
        return [utils.get_ref_name(ref).lower() for ref in schema.get_all_refs()]

    def parse_paths(self, interfaces):
        """
        Once we have constructed graph, we also want to save Operation relevant details to each node
        We would go through Operation interfaces, and add details about resource-operation in Resource Nodes
        """

        ref_op_map = {
            "consumer": "add_consumer",
            "producer": "add_producer",
            "destructor": "add_destructor"
        }

        for operation in interfaces:
            op_id = operation.op_id
            ref_graph = {}

            # Producers were already marked before in the work cycle, so we can save lots of work by just using them
            for ref in operation.producer_references:
                ref_graph[ref] = "producer"

            # We got producers, so we now just need to look in Request params, to search for consumers and destroyers
            self.parse_request_parameters(operation, ref_graph)

            for ref, ref_op in ref_graph.items():
                resource_node = self.nodes.get(self.get_associated_resource_for_ref(ref))
                if resource_node:
                    getattr(resource_node, ref_op_map.get(ref_op))(op_id)

        self.remove_dependent_producers()

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
                if self.is_delete_resource(operation, parameter):
                    ref_graph[resource] = "destructor"
                else:
                    # This time, it is Path Params, so we are sure that is is consumer
                    ref_graph[resource] = "consumer"

            if parameter.get(constants.IN_) == constants.BODY_PARAM:
                request_refs = self.get_schema_refs(parameter)

                # If it is already claimed as producer/consumer, then respect that
                for ref in request_refs:
                    if ref not in ref_graph:
                        ref_graph[ref] = "consumer"

    @staticmethod
    def is_delete_resource(operation, parameter):
        return (
            operation.method == constants.DELETE and
            parameter.get(constants.PARAMETER_NAME) == operation.url_end_parameter()
        )

    def remove_dependent_producers(self):
        """
        Consider a definition:
        A:
            id
            B:
                id
                name
            name

        here, we say that A is dependent on B, since any resource which consumes A, must first know about B.

        In this case, any consumer of A should NOT count as producer of B.
        This function finds such connections, and remove these attributes
        """

        visited = {_node: self.WHITE for _node in self}

        for node in visited.keys():
            if visited[node] == self.WHITE:
                self.remove_dependent_producers_helper(node, visited)

    def remove_dependent_producers_helper(self, resource, visited):

        child_consumers = set()

        for adj_resource in resource.get_connections():
            child_consumers.update(self.remove_dependent_producers_helper(adj_resource, visited))

        # Remove all producers which consume Children
        resource.producers -= child_consumers

        visited[resource] = self.BLACK

        return child_consumers | resource.consumers


class SwaggerResourceValidator:

    def __init__(self, resource_graph, interfaces):
        self.resource_graph = resource_graph
        self.interfaces = interfaces

    def get_resources_with_no_producers(self):
        resources = set()

        for operation in self.interfaces:
            for parameter in operation.parameters.values():
                resource = parameter.get(constants.RESOURCE)
                if resource and parameter.get(constants.IN_) == constants.PATH_PARAM:
                    resources.add(resource)

        no_producer_resources = set()

        for resource in self.resource_graph:
            if resource.key in resources:
                resource_pure_producers = resource.producers - resource.consumers
                if not resource_pure_producers:
                    no_producer_resources.add(resource.key)

        return no_producer_resources

    def validate(self):

        no_producer_resources = self.get_resources_with_no_producers()

        if no_producer_resources:
            print(
                f"\nHINT: ATLAS cannot find API which produces the resources: '{', '.join(no_producer_resources)}'. "
                f"You may need to add their DB mapping in conf/resource_mapping.yaml\n"
            )
