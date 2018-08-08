import itertools
from functools import wraps
from string import Formatter

from scripts.resources.generators import Resource


class ResourceDecorator:

    def __init__(self):
        self.func_args = tuple()
        self.func_kwargs = dict()
        self.resource = None
        self.klass = None
        self.url = None

    def get_resource_class(self):
        return Resource(self.resource)

    def inner(self, func):

        @wraps(func)
        def wrapper(*f_args, **f_kwargs):
            self.update_url(url=self.url, resources=self.klass.get_resources())
            f_kwargs.update(self.func_kwargs)
            return func(*f_args, **f_kwargs)

        return wrapper

    def func_init(self, *args, **kwargs):
        self.func_args = args
        self.func_kwargs = kwargs

    def add_resource_to_args(self, resources):
        if not isinstance(resources, tuple):
            resources = (resources,)
        self.func_args = tuple(itertools.chain(self.func_args, resources))

    def update_url(self, url, resources):
        # Formatter returns an iterable, and we only care about first value
        str_key = Formatter().parse(url).__next__()[1]
        self.func_kwargs["format_url"] = url.format(**{str_key: resources})

    def fetch(self, resource, url, *args, **kwargs):
        self.func_init(args, kwargs)
        self.resource = resource
        self.url = url
        self.klass = self.get_resource_class()
        return self.inner
