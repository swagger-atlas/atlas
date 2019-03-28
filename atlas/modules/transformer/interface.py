import re

from atlas.modules import (
    constants,
    exceptions,
)


class OpenAPITaskInterface:
    """
    This serves as interface between OpenAPI Operation and several ATLAS classes
    """

    def __init__(self):

        self._parameters = {}
        self._func_name = ""
        self._method = ""
        self._url = ""
        self._tags = []
        self._responses = {}
        self._consumes = [constants.JSON_CONSUMES]
        self._dependent_resources = set()

        self._resource_producers = set()
        self._producer_references = set()

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    @property
    def func_name(self):
        return self._func_name

    @func_name.setter
    def func_name(self, value):
        self._func_name = re.sub(r"\.", "_", value)

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        if value not in constants.VALID_METHODS:
            raise exceptions.ImproperSwaggerException(f"Invalid method {self.method} for {self.url}")
        self._method = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        if not isinstance(value, list):
            raise exceptions.ImproperSwaggerException("Tags must be Array - Op ID {}".format(self.func_name))
        self._tags = value

    @property
    def responses(self):
        return self._responses

    @responses.setter
    def responses(self, value):
        valid_responses = {}
        for status_code, config in value.items():
            if isinstance(status_code, str):
                if status_code == constants.DEFAULT:
                    valid_responses[status_code] = config
                else:
                    try:
                        status_code = int(status_code)
                    except (ValueError, TypeError):
                        raise exceptions.ImproperSwaggerException(f"Status Code of {config} must be default/int string")

            if isinstance(status_code, int) and 200 <= status_code < 300:
                valid_responses[str(status_code)] = config

        self._responses = valid_responses

    @property
    def mime(self):
        lowest_idx = len(constants.CONSUME_PRIORITY)
        mime = ""
        for element in self._consumes:
            mime_idx = constants.CONSUME_PRIORITY.index(element)
            if mime_idx < lowest_idx:
                lowest_idx = mime_idx
                mime = element
        return mime

    @property
    def consumes(self):
        return self._consumes

    @consumes.setter
    def consumes(self, value: list):
        if value:
            self._consumes = [element for element in value if element in constants.CONSUME_PRIORITY]

    def url_end_parameter(self):
        """
        Find the Path parameter which appears at the end of the URL.
        If there is no such parameter, returns None
        """

        ret_parameter = None

        url_fragments = [fragment for fragment in self._url.split("/") if fragment]
        last_fragment = url_fragments[-1]

        if last_fragment.startswith("{") and last_fragment.endswith("}"):
            ret_parameter = last_fragment[1: -1]

        return ret_parameter

    @property
    def dependent_resources(self):
        return self._dependent_resources

    @dependent_resources.setter
    def dependent_resources(self, value: set):
        self._dependent_resources = value

    @property
    def op_id(self):
        return f"{self.method.upper()} {self.url}"

    @property
    def resource_producers(self):
        return self._resource_producers

    @resource_producers.setter
    def resource_producers(self, value):
        self._resource_producers = value

    @property
    def producer_references(self):
        return self._producer_references

    @producer_references.setter
    def producer_references(self, value):
        self._producer_references = value
