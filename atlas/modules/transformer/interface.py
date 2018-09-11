from atlas.modules import (
    constants,
    exceptions,
)


class OpenAPITaskInterface:
    """
    This serves as interface between OpenAPI Operation and Load Test Tasks
    """

    def __init__(self):

        self._parameters = []
        self._func_name = ""
        self._method = ""
        self._url = ""

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
        self._func_name = value

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        if value not in constants.VALID_METHODS:
            raise exceptions.ImproperSwaggerException("Invalid method {} for {}".format(self.method, self.url))
        self._method = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value
