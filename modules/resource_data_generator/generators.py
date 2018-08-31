import importlib
import os

from modules import exceptions, utils, mixins
from modules.resource_data_generator import constants as resource_constants
from modules.database import client as db_client
from settings.conf import settings


class ResourceMixin(mixins.ProfileMixin, mixins.YAMLReadWriteMixin):
    """
    Base Resource Mixin
    """


class ResourceMap(ResourceMixin):
    """
    Parse over Resource Map and create a cache of Resources
    """

    def __init__(self, profiles=None):

        self.map = self.read_file_from_output(settings.MAPPING_FILE)
        self.limit = 50
        self.client = db_client.Client()

        self.profiles = profiles or []
        self.active_profile_config = None

    def inherit_resources(self, config):
        """
        Inherit resources as far as we want
        """

        final_config = config

        while True:
            parent_resource = config.pop(resource_constants.RESOURCE, None)

            if parent_resource:
                parent = self.map.get(parent_resource)
                if not parent:
                    raise exceptions.ResourcesException("Can not find Parent {}".format(parent_resource))
                final_config = {**parent, **config}
                config = parent
            else:
                break

        return final_config

    def read_for_profile(self, resources, global_settings):

        for resource, config in self.map.items():
            # We have already constructed this resource, so ignore this and move
            if resource in resources:
                continue

            config = self.inherit_resources(config)

            source = config.get(resource_constants.SOURCE, resource_constants.DB_TABLE)

            if source == resource_constants.DB_TABLE:
                result = self.parse_db_source(config, global_settings)
            elif source == resource_constants.SCRIPT:
                result = self.parse_python_source(config)
            else:
                raise exceptions.ResourcesException("Incorrect source defined for {}".format(resource))

            if not isinstance(result, (list, tuple, set)):
                raise exceptions.ResourcesException("Result for {} must be Built-in iterable".format(resource))

            resources[resource] = set(result)

    def parse(self):

        global_settings = self.map.pop(resource_constants.GLOBALS, {})

        for name, config in self.get_profiles().items():
            resources = self.read_file(
                self.get_profile_resource_name(name, config), {},
                os.path.join(settings.OUTPUT_FOLDER, settings.RESOURCES_FOLDER)
            )
            self.active_profile_config = config
            self.read_for_profile(resources, global_settings)
            self.write_file(
                self.get_profile_resource_name(name, config), resources,
                os.path.join(settings.OUTPUT_FOLDER, settings.RESOURCES_FOLDER)
            )

    def construct_fetch_query(self, table, column, filters):
        """
        Construct a simple SQL Fetch Query
        """
        select_statement = "select {column} from {table}".format(column=column, table=table)
        filter_statement = "where {filters}".format(filters=filters) if filters else ""
        limit_statement = "limit {limit}".format(limit=self.limit)

        return " ".join([select_statement, filter_statement, limit_statement])

    def parse_db_source(self, config, global_settings):

        # First check if raw SQL is provided
        sql = config.get(resource_constants.SQL)
        mapper = config.get(resource_constants.MAPPER, global_settings.get(resource_constants.MAPPER))

        client_func = self.client.fetch_rows

        func = None
        if mapper:
            func = self.get_function_from_mapping_file(mapper)

        if not sql:
            # If Raw SQL is not provided, then we need to construct query
            sql = self.construct_query(config, global_settings)
            client_func = self.client.fetch_ids

        # Query should be formatted according to Profile configuration
        return client_func(sql=sql.format(**self.active_profile_config), mapper=func)

    def construct_query(self, config, global_settings):
        table = config.get(resource_constants.TABLE)

        if not table:
            raise exceptions.ResourcesException("Table not defined for {}".format(config))

        column = config.get(resource_constants.COLUMN, resource_constants.DEFAULT_COLUMN)
        filters = config.get(resource_constants.FILTERS, global_settings.get(resource_constants.FILTERS))

        return self.construct_fetch_query(table, column, filters)

    @staticmethod
    def get_function_from_mapping_file(func_name):
        map_hook_file = "{}.{}".format(utils.get_input_project_module(), settings.RES_MAPPING_HOOKS_FILE)[:-len(".py")]
        func = getattr(importlib.import_module(map_hook_file), func_name)

        if not func:
            raise exceptions.ResourcesException("Function {} not defined in Map Hooks File".format(func_name))

        return func

    def parse_python_source(self, config):

        func_name = config.get(resource_constants.FUNCTION)

        if not func_name:
            raise exceptions.ResourcesException("Function must be declared for {}".format(config))

        func = self.get_function_from_mapping_file(func_name)

        args = config.get(resource_constants.ARGS, ())

        if not isinstance(args, (tuple, list)):
            raise exceptions.ResourcesException("Function {} Args should be tuple/list".format(func_name))

        kwargs = config.get(resource_constants.KWARGS, {})

        if not isinstance(kwargs, dict):
            raise exceptions.ResourcesException("Function {} Keyword Args should be dict".format(func_name))

        return func(*args, **kwargs)

    def get_profiles(self):
        profiles = self.read_file_from_input(settings.PROFILES_FILE, {})

        if self.profiles:
            profile_to_read = set(self.profiles)
            profiles = {key: val for key, val in profiles if key in profile_to_read}

        return profiles


if __name__ == "__main__":
    res_map = ResourceMap()
    res_map.parse()
