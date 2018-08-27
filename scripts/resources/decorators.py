import itertools
from functools import wraps

from scripts import (
    constants,
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
        return self.generator_class.get_fake_mapper(config)

    def update_data(self, config):

        data_body = {}

        for item_name, item_config in config.items():
            fake_func = self.get_gen_function(item_config)

            if fake_func:
                data_body[item_name] = fake_func(self.generator_class, item_config)

        self.func_kwargs["body"] = data_body

    def get_generator_class(self, specs=None):
        return FakeData(specs)

    def body(self, resource, *args, **kwargs):
        self.func_init(args, kwargs)
        self.resource = resource
        self.generator_class = self.get_generator_class(kwargs.get("specs"))
        return self.inner

    def func_init(self, *args, **kwargs):
        self.func_args = args
        self.func_kwargs = kwargs


class ResourceDecorator(FakeDataDecorator):
    """
    Should be only used to decorate Task Set Class Methods
    """

    def __init__(self):
        super().__init__()
        self.url = None
        self.param_name = ""

    def get_generator_class(self, specs=None):
        return Resource(self.resource)

    def inner(self, func):

        @wraps(func)
        def wrapper(*f_args, **f_kwargs):
            instance = f_args[0]    # First argument of methods must be self
            profile = getattr(instance, "profile")
            self.func_kwargs[self.param_name] = self.generator_class.get_resources(profile=profile)
            f_kwargs.update(self.func_kwargs)
            return func(*f_args, **f_kwargs)

        return wrapper

    def update_params(self, config, profile, specs=None):

        data_body = {}

        for item_name, item_config in config.items():
            resource = item_config.get(constants.RESOURCE)

            if resource:
                data_body[item_name] = self.generator_class.get_resources(profile=profile)
            else:
                generator_class = super().get_generator_class(specs)
                fake_func = generator_class.get_fake_mapper(item_config)

                if fake_func:
                    data_body[item_name] = fake_func(generator_class, item_config)

        self.func_kwargs["body"] = data_body

    def add_resource_to_args(self, resources):
        if not isinstance(resources, tuple):
            resources = (resources,)
        self.func_args = tuple(itertools.chain(self.func_args, resources))

    def update_url(self, url, resources):
        self.func_kwargs[self.param_name] = url.format_map(utils.StringDict(**{self.param_name: resources}))

    def fetch(self, resource, name, *args, **kwargs):
        self.func_init(args, kwargs)
        self.resource = resource
        # self.url = url
        self.param_name = name
        self.generator_class = self.get_generator_class()
        return self.inner


def fetch(resource, name, *args, **kwargs):
    res_obj = ResourceDecorator()
    return res_obj.fetch(resource, name, *args, **kwargs)


def body(config, profile, specs=None):
    res_obj = ResourceDecorator()
    res_obj.generator_class = res_obj.get_generator_class(specs)
    res_obj.update_params(config, profile, specs)
    return res_obj.func_kwargs["body"]


def formatted_url(url, query_config, path_config, profile):
    fake_obj = FakeDataDecorator()
    res_obj = ResourceDecorator()
    res_obj.generator_class = res_obj.get_generator_class()
    fake_obj.generator_class = fake_obj.get_generator_class()
    fake_obj.update_data(path_config)
    url = url.format_map(utils.StringDict(**fake_obj.func_kwargs["body"]))
    res_obj.update_params(query_config, profile)
    # Note that since we use params argument in Requests library, we only ever support "multi" argument for Query Params
    # This also means that we on surface do no support parameters without value
    return url, res_obj.func_kwargs["body"]


def header(config):
    fake_obj = FakeDataDecorator()
    fake_obj.generator_class = fake_obj.get_generator_class()
    fake_obj.update_data(config)
    return fake_obj.func_kwargs["body"]
