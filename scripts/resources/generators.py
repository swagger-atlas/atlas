import importlib
from io import open
import os

import random
import yaml

from scripts import exceptions
from scripts.resources import constants as resource_constants
from scripts.database import client as db_client
from settings.conf import settings


class ResourceReadWriteMixin:

    def __init__(self):
        self.resources = {}

    @property
    def project_path(self):
        return os.path.join(settings.BASE_DIR, settings.PROJECT_FOLDER_NAME, settings.PROJECT_NAME)

    def read_resources(self):
        _file = os.path.join(self.project_path, settings.RESOURCE_POOL_FILE)

        try:
            with open(_file) as resource_file:
                ret_stream = yaml.safe_load(resource_file)
        except FileNotFoundError:
            ret_stream = {}

        return ret_stream or {}

    def write_resources(self):
        _file = os.path.join(self.project_path, settings.RESOURCE_POOL_FILE)

        with open(_file, 'a+') as auto_write_file:
            yaml.dump(self.resources, auto_write_file, default_flow_style=False)


class Resource(ResourceReadWriteMixin):

    def __init__(self, resource_group_name, *args, items=1, flat_for_single=True, **kwargs):
        """
        :param resource_group_name:
        :param items: Number of resources to fetch
        :param flat_for_single: (Boolean)
            For Single resource: (i.e. items==1)
                True: Simplest format
                False: As Iterator
            For multiple resources:
                It is always false
        """

        # Args/kwargs are there to cover function call with spurious arguments
        # Since Class could be instantiated on run-time with variable number of arguments
        # We don't want to raise error to deal with extra arguments

        self.resource_name = resource_group_name
        self.items = items
        self.flat_result = flat_for_single if items == 1 else False

        super().__init__()

    def resource_set(self):
        group = self.resources.get(self.resource_name)
        resources = []
        if group and len(group) >= self.items:
            resources = self.get_random_element_from_set(group)
        return resources

    def get_random_element_from_set(self, resource_set):
        elements = random.sample(resource_set, self.items)
        return [element[resource_constants.RESOURCE_VALUE] for element in elements]

    def get_resource_from_db(self):
        """
        :return:
        """
        # TODO

    def add_resources_to_pool(self, resource_data):
        res = self.resources[self.resource_name]
        for data in resource_data:
            res.append({resource_constants.RESOURCE_VALUE: data})
        self.write_resources()

    def get_resources(self):

        if not self.resources:
            self.resources = self.read_resources()

        # First try Resources from Pre-built cache
        resources = self.resource_set()

        # If un-successful fetch from db,
        resources = resources or self.get_resource_from_db()

        # If still un-successful (Resource do not exist in DB also)
        if not resources:
            raise exceptions.ResourcesException("Resource Not found - {}".format(self.resource_name))

        if self.flat_result:
            resources = resources[0]

        return resources


class ResourceMap(ResourceReadWriteMixin):
    """
    Parse over Resource Map and create a cache of Resources
    """

    def __init__(self):

        self.map = self.read_mapping()
        self.limit = 50
        self.client = db_client.Client()

        super().__init__()

    @property
    def project_module(self):
        return "{proj_folder}.{name}".format(proj_folder=settings.PROJECT_FOLDER_NAME, name=settings.PROJECT_NAME)

    def read_mapping(self):
        _file = os.path.join(self.project_path, settings.MAPPING_FILE)

        with open(_file) as open_api_file:
            ret_stream = yaml.safe_load(open_api_file)

        return ret_stream

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

    def parse(self):

        global_settings = self.map.pop(resource_constants.GLOBALS, {})
        self.resources = self.read_resources()

        for resource, config in self.map.items():
            # We have already constructed this resource, so ignore this and move
            if resource in self.resources:
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

            self.resources[resource] = [{resource_constants.RESOURCE_VALUE: res} for res in result]
        self.write_resources()

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

        func = None
        if mapper:
            func = self.get_function_from_mapping_file(mapper)

        if sql:
            return self.client.fetch_rows(sql, mapper=func)

        table = config.get(resource_constants.TABLE)

        if not table:
            raise exceptions.ResourcesException("Table not defined for {}".format(config))

        column = config.get(resource_constants.COLUMN, resource_constants.DEFAULT_COLUMN)
        filters = config.get(resource_constants.FILTERS, global_settings.get(resource_constants.FILTERS))

        sql = self.construct_fetch_query(table, column, filters)
        return self.client.fetch_ids(sql, mapper=func)

    def get_function_from_mapping_file(self, func_name):
        map_hook_file = "{}.{}".format(self.project_module, settings.RES_MAPPING_HOOKS_FILE)[:-len(".py")]
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


if __name__ == "__main__":
    res_map = ResourceMap()
    res_map.parse()
