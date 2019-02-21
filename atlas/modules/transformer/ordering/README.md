Before going into that, let us consider the following definitions and associated data structures:

References
----------

Swagger responses, and parameters can contain references to swagger definitions
These swagger definitions in turn can be nested, i.e. contain reference to other definitions

Our code refer to references and definitions inter-changeably

###### Data structures:

- *Reference*:
    Reference keeps track of all definitions, and if this definition contains other definitions
    In case a reference has multiple resources attached to them, assign one resource as primary one.

Resources
---------

ATLAS needs to identify entities
- which binds operation together
- for which we cannot generate random data


Examples of such entities are:
- URL Path Params:
    `GET /students/{id}`
    Here we cannot randomly generate `id`, since that will most likely result in 404

- Specific definition fields
    ```yaml
    student:
        type: object
        properties:
            id:
                type: integer
                readOnly: true
            name:
                type: string
    ```

    Here `id` is a field which can be used as input for another Operations, and would bind several op
    together.

Before running ordering, ATLAS would have identified all such entities and marked them as resources.
Further, we ensure that each resource is bound to at least one definition, and if not, we create one.

###### Data structures:

- *Resource Node*:
    Resource Node contains information about
     - which resource it represents,
     - Operations which will produce this resource
     - Operations which will consume this resource
     - Operations which will destroy this resource

- *Resource graph*:

    Using reference/definition connections with each other, we construct resource graph:
    - Each definition is transformed to its primary resource
    - Edges between definitions are carried as it is

    Further, we traverse the Open API Specification, and add information to resource nodes

Operation
---------

A combination of METHOD and URL represents a single operation.
One operation represents one API.

Our goal is to arrange the operations in a manner such that following conditions are satisfied:
- Any operation which consumes X resource must occur after operations which produce X
- Any operation which destroys X resource must occur after operations which produce or consume X
- If X resource is dependent on Y, then producers of Y must occur before producers of X.
- If X resource is dependent on Y, then consumers of Y must occur before consumers of X.

###### Data Structures

- Operation Node
    Standard Graph Node

- Operation Graph
    Operation graph is now constructed by transforming resource graph into op. graph.
    This transformation is done on the basis of the dependencies outlined above.

    Once this graph is constructed, it is topologically sorted to give the required operation order
