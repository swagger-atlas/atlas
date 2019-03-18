from atlas.modules import constants, utils
from atlas.conf import settings


class SwaggerOutputWriter:

    @staticmethod
    def write(log, problem, solution):
        solution = solution or ""

        if log in {"warning", "error"}:
            print(f"Swagger Validation {log}: {problem}. {solution}")

    def error(self, problem, solution=None):
        solution = solution or ""
        self.write("error", problem, solution)

    def warning(self, problem, solution=None):
        solution = solution or ""
        self.write("warning", problem, solution)

    def debug(self, problem, solution=None):
        solution = solution or ""
        self.write("debug", problem, solution)


class Swagger:

    def __init__(self, specs):
        self.specs = specs
        self.writer = SwaggerOutputWriter()

        self.resources = set()

    def validate_path(self):

        base_path = self.specs.get(constants.BASE_PATH)
        if not base_path:
            self.writer.error("Base Path not defined", "Please update swagger or define it in settings")

        schemes = self.specs.get(constants.SCHEMES)
        if not schemes:
            self.writer.error("Scheme not defined", "Please update swagger or define it in settings")
        if not isinstance(schemes, list):
            self.writer.error("Schemes must be a list instance")

        host = self.specs.get(constants.HOST)
        if not host:
            self.writer.error("Host not defined", "Please update swagger or define it in settings")

    def validate_consumes(self):

        consumes = set(self.specs.get(constants.CONSUMES, []))

        valid_consumes = set(constants.CONSUME_PRIORITY)
        if not valid_consumes.intersection(consumes):
            self.writer.warning("No valid Consumers")

    def get_all_resources(self):
        """
        Get all resources from definitions
        """

        definitions = self.specs.get(constants.DEFINITIONS, {})

        for definition, config in definitions.items():
            _type = config.get(constants.TYPE)

            if _type == constants.OBJECT:
                properties = config.get(constants.PROPERTIES, {})
                for name, name_config in properties.items():
                    if name in settings.SWAGGER_REFERENCE_FIELD_RESOURCE_IDENTIFIERS:
                        resource = name_config.get(constants.RESOURCE, utils.convert_to_snake_case(definition))
                        if resource:
                            self.resources.add(resource)

    def validate_parameters(self, parameters, url, method=None):

        for parameter in parameters:

            ref = parameter.get(constants.REF)
            if ref:
                parameter = self.resolve_reference(ref)

            name = parameter.get(constants.PARAMETER_NAME)
            in_ = parameter.get(constants.IN_)
            # For body parameters, type is usually skipped and schema is given
            type_ = parameter.get(constants.TYPE, constants.OBJECT)
            required = parameter.get(constants.REQUIRED, False)

            if not (name and in_ and type_):
                key = f"URL {url}: {method}" if method else f"URL {url}"
                self.writer.error(f"{key} has invalid parameter configuration")
                return

            param = Parameter(parameter, name, in_, type_, required)
            param.validate(url, self.resources)

    def validate(self):

        self.validate_path()
        self.validate_consumes()

        self.get_all_resources()

        operations = self.specs.get(constants.PATHS, {})
        for url, config in operations.items():
            for method, method_config in config.items():
                if method in constants.VALID_METHODS:
                    _op = Operation(url, method, method_config)
                    _op.validate()
                    self.validate_parameters(_op.get_params(), url, method)
                elif method == constants.PARAMETERS:
                    self.validate_parameters(method_config, url)

    def resolve_reference(self, reference_name):
        return utils.resolve_reference(self.specs, reference_name)


class Operation:

    def __init__(self, url, method, config):
        self.url = url
        self.method = method
        self.config = config
        self.writer = SwaggerOutputWriter()

    def validate(self):

        # Check for responses
        responses = self.config.get(constants.RESPONSES, {})
        if not responses:
            self.writer.error(
                f"Responses not defined for {self.url}: {self.method}",
                "Please update swagger or define it in settings"
            )
            return

        valid_status_codes = False
        for code, config in responses.items():
            response = Response(self.url, self.method, code, config)
            if code == "default":
                valid_status_codes = True
                response.validate()
            elif 200 <= int(code) < 300:
                valid_status_codes = True
                if int(code) != 204:
                    response.validate()

        if not valid_status_codes:
            self.writer.error(f"At least one success code must be defined for {self.url}: {self.method}")

    def get_params(self):
        return self.config.get(constants.PARAMETERS, [])


class Parameter:

    def __init__(self, config, name, _in, _type, required=False):
        self.name = name
        self.in_ = _in
        self.type = _type
        self.required = required
        self.config = config

        self.writer = SwaggerOutputWriter()

    def validate(self, url, resources):

        if self.in_ in constants.URL_PARAMS:
            resource = self.config.get(
                constants.RESOURCE, utils.extract_resource_name_from_param(self.name, url, self.in_)
            )
            if resource not in resources:
                self.writer.debug(f"{self.name} parameter resolves to resource {resource}."
                                  f" ATLAS will either generate one or pick up from resource_mapping")


class Response:

    def __init__(self, url, method, status_code, config):
        self.code = status_code
        self.config = config
        self.url = url
        self.method = method
        self.writer = SwaggerOutputWriter()

    def validate(self):

        schema = self.config.get(constants.SCHEMA, {})
        if not schema:
            self.writer.warning(f"Response Schema not defined for {self.url}: {self.method} - Status Code: {self.code}")

        elif not self.get_ref(schema):
            self.writer.warning(
                f"Response Schema should be defined via reference: {self.url}: {self.method} - Status Code: {self.code}"
            )

    def get_ref(self, schema):

        ref = schema.get(constants.REF, {})
        if ref:
            return True

        ref_found = False

        _type = schema.get(constants.TYPE)
        if _type == constants.ARRAY:
            items = schema.get(constants.ITEMS)
            if isinstance(items, dict):
                ref_found = self.get_ref(items)
        elif _type == constants.OBJECT:
            properties = schema.get(constants.PROPERTIES, {})
            for prop_config in properties.values():
                ref_found = ref_found or self.get_ref(prop_config)

        return ref_found
