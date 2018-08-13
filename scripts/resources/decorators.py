import itertools
from functools import wraps
from string import Formatter

from scripts import (
    constants as swagger_constants,
    exceptions,
    utils
)
from scripts.resources.generators import Resource
from scripts.resources.data_mapper import FakeData


class FakeDataDecorator:

    def __init__(self):
        self.func_args = tuple()
        self.func_kwargs = dict()
        self.generator_class = None
        self.resource = None

    def inner(self, func):

        @wraps(func)
        def wrapper(*f_args, **f_kwargs):
            self.update_data(self.resource)
            f_kwargs.update(self.func_kwargs)
            return func(*f_args, **f_kwargs)

        return wrapper

    def get_gen_function(self, config):
        item_type = config.get(swagger_constants.TYPE)

        # TODO: Reference handling
        if not item_type:
            raise exceptions.ImproperSwaggerException("Item type must be defined")

        item_format = config.get(swagger_constants.FORMAT)

        fake_func = self.generator_class.FAKE_MAP.get((item_type, item_format), None)

        # If it did not match, try to match any format
        if not fake_func:
            fake_func = self.generator_class.FAKE_MAP.get((item_type, "$any"), None)

        return fake_func

    def update_data(self, config):

        body = {}

        for item_name, item_config in config.items():
            fake_func = self.get_gen_function(item_config)

            if fake_func:
                body[item_name] = fake_func(self.generator_class, item_config)

        self.func_kwargs["body"] = body

    def get_generator_class(self):
        return FakeData()

    def body(self, resource, *args, **kwargs):
        self.func_init(args, kwargs)
        self.resource = resource
        self.generator_class = self.get_generator_class()
        return self.inner

    def func_init(self, *args, **kwargs):
        self.func_args = args
        self.func_kwargs = kwargs


class ResourceDecorator(FakeDataDecorator):

    def __init__(self):
        super().__init__()
        self.url = None

    def get_generator_class(self):
        return Resource(self.resource)

    def inner(self, func):

        @wraps(func)
        def wrapper(*f_args, **f_kwargs):
            self.update_url(url=self.url, resources=self.generator_class.get_resources())
            f_kwargs.update(self.func_kwargs)
            return func(*f_args, **f_kwargs)

        return wrapper

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
        self.generator_class = self.get_generator_class()
        return self.inner


def fetch(resource, url, *args, **kwargs):
    res_obj = ResourceDecorator()
    return res_obj.fetch(resource, url, *args, **kwargs)


def body(config):
    fake_obj = FakeDataDecorator()
    fake_obj.generator_class = fake_obj.get_generator_class()
    fake_obj.update_data(config)
    return fake_obj.func_kwargs["body"]


def formatted_url(url, query_config, path_config):
    fake_obj = FakeDataDecorator()
    fake_obj.generator_class = fake_obj.get_generator_class()
    fake_obj.update_data(path_config)
    url.format_map(utils.StringDict(**fake_obj.func_kwargs["body"]))
    fake_obj.update_data(query_config)
    return fake_obj.func_kwargs["body"]
