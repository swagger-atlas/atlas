import random

from modules import exceptions
from modules.resource_data_generator.generators import ResourceMixin
from settings.conf import settings


class Resource(ResourceMixin):

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

        self.resources = {}

        self.profiles = self.read_file_from_input(settings.PROFILES_FILE, {})
        self.active_profile = ""

    @property
    def profile_config(self):
        return self.profiles.get(self.active_profile)

    @property
    def profile_resource(self):
        return self.get_profile_resource_name(self.active_profile, self.profile_config)

    def resource_set(self):
        resource_set = self.resources.get(self.resource_name, [])

        if len(resource_set) > self.items:
            resource_set = random.sample(resource_set, self.items)

        return list(resource_set)

    def get_resources(self, profile):

        self.active_profile = profile
        self.resources = self.read_file_from_output(
            self.profile_resource, {}, project_sub_folder=settings.RESOURCES_FOLDER
        )

        resources = self.resource_set()

        if not resources:
            raise exceptions.ResourcesException("Resource Pool Not found for - {}".format(self.resource_name))

        if self.flat_result:
            resources = resources[0]

        return resources
