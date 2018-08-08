from collections import defaultdict

import random

from scripts import exceptions
from scripts.resources import constants as resource_constants
from scripts.database import client as db_client


RESOURCES = defaultdict(set, {
    # "user": {53859, 54001, 53775},
    "session": {1, 2, 3, 4}
})


class Resource:

    def __init__(self, resource_group_name, items=1, flat_for_single=True, *args, **kwargs):
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

    def resource_set(self):
        group = RESOURCES.get(self.resource_name)
        resources = []
        if group and len(group) >= self.items:
            resources = self.get_random_element_from_set(group)
        return resources

    def get_random_element_from_set(self, resource_set):
        return random.sample(resource_set, self.items)

    def get_resource_from_db(self):
        """
        :return:
        """
        # TODO

    def add_resources_to_pool(self, resource_data):
        res = RESOURCES[self.resource_name]
        for data in resource_data:
            res.add(data)

    def get_resources(self):

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


class ResourceMap:
    """
    Parse over Resource Map and create a cache of Resources
    """

    def __init__(self, resource_map):
        self.map = resource_map
        self.limit = 50

        self.client = db_client.Client()

    def parse(self):
        for resource, config in self.map.items():
            table = config.get(resource_constants.TABLE)

            if not table:
                raise exceptions.ResourcesException("Table not defined for {}".format(resource))

            column = config.get(resource_constants.COLUMN, resource_constants.DEFAULT_COLUMN)

            if resource not in RESOURCES:
                sql = self.construct_fetch_query(table, column)
                result = self.client.fetch_ids(sql)
                RESOURCES[resource] = result

    def construct_fetch_query(self, table, column):
        """
        Construct a simple SQL Fetch Query
        """

        return "select {column} from {table} limit {limit}".format(column=column, table=table, limit=self.limit)
