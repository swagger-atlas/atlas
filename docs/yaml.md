YAML
======
YAML stands for YAML Ain't Markup Language


Resources
-----
- https://pyyaml.org/wiki/PyYAMLDocumentation


Writing YAML
----
- Any valid JSON is valid YAML. YAML is super-set of JSON.
- Swagger definitions are most likely to be in both YAML and JSON, so you can take an example of YAML from there


Why YAML
----
- Shorter than JSON in terms of line, as well as easier to write
- JSON only supports lists and dictionaries as complex type. We may need much more than that esp. when defining function arguments
- YAML can theoretically be used to represent any complex Python object


Best Practices
----
- Always use `safe_load` with YAML since simple `load` can be used to execute any arbitrary python code
