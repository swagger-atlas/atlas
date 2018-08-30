from scripts import (
    constants,
    utils
)
from scripts.data_provider.locust.resource_providers import Resource
from scripts.data_provider.locust.fake_providers import FakeData


class DataMapper:

    def __init__(self, profile=None, specs=None):
        self.profile = profile
        self.specs = specs

    def get_resource(self, resource):
        return Resource(resource).get_resources(profile=self.profile)

    def get_fake_data(self, config):
        generator_class = FakeData()
        fake_func = generator_class.get_fake_mapper(config)

        ret = None

        if fake_func:
            ret = fake_func(generator_class, config)

        return ret

    def generate_data(self, config):

        data_body = {}

        for item_name, item_config in config.items():

            # First, resolve references
            ref = item_config if item_name == constants.REF else item_config.get(constants.REF)

            if ref:
                data_body[item_name] = self.generate_data(
                    utils.resolve_reference(self.specs, ref).get(constants.PROPERTIES, {})
                )
                continue    # We generated the data already, move on to next once

            # Do not generate data for Read-only fields
            read_only = item_config.get(constants.READ_ONLY, False)
            if read_only:
                continue

            resource = item_config.get(constants.RESOURCE)

            value = self.get_resource(resource) if resource else self.get_fake_data(item_config)

            if value:
                data_body[item_name] = value

        return data_body

    def format_url(self, url, query_config, path_config):
        path_params = self.generate_data(path_config)
        url = url.format_map(utils.StringDict(**path_params))
        query_params = self.generate_data(query_config)
        return url, query_params
