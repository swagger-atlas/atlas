import base64
from datetime import timezone
import random

from faker import Faker

from modules import (
    constants,
    utils,
    exceptions
)
from modules.resource_data_generator.generators import ResourceMixin
from settings.conf import settings

# This is arbitrary limit. Test cases should not break with change of this limit.
# Parameters which are sensitive to this should define their own min/max limits
LIMIT = 10 ** 6


class Provider:

    def __init__(self, profile=None):
        self.profile = profile

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


class FakeData:

    def __init__(self):
        self.fake = Faker()

    def get_fake_mapper(self, config):

        item_type = config.get(constants.TYPE)

        if not item_type:
            raise exceptions.ImproperSwaggerException("Item type must be defined")

        item_format = config.get(constants.FORMAT)

        fake_func = self.FAKE_MAP.get((item_type, item_format), None)

        # If it did not match, try to match any format
        if not fake_func:
            fake_func = self.FAKE_MAP.get((item_type, "$any"), None)

        return fake_func

    @staticmethod
    def get_enum(config):
        enum_options = config.get(constants.ENUM, [])

        choice = None

        if enum_options:
            choice = random.choice(enum_options)

        return choice

    @staticmethod
    def get_range(config):
        minimum = config.get(constants.MINIMUM, -LIMIT)
        maximum = config.get(constants.MAXIMUM, LIMIT)

        if config.get(constants.MIN_EXCLUDE, False):
            minimum += 1

        if config.get(constants.MAX_EXCLUDE, False):
            maximum -= 1

        if minimum > maximum:
            raise exceptions.ImproperSwaggerException("Minimum cannot be lower than maximum")

        return minimum, maximum

    def get_integer(self, config):
        return (
            self.get_enum(config)
            or random.randint(*self.get_range(config)) * config.get(constants.MULTIPLE_OF, 1)
        )

    def get_float(self, config):

        # Short-circuit return
        num = self.get_enum(config)
        if num:
            return num

        minimum, maximum = self.get_range(config)
        left_side = random.randint(minimum, maximum)
        right_side = round(random.random(), 2)

        final_number = left_side + right_side

        if final_number > maximum:
            final_number = float(maximum)

        if final_number < minimum:
            final_number = float(minimum)

        return final_number

    @staticmethod
    def get_options(config):
        """
        Swagger supports following options:
            - MinLength
            - MaxLength
            - Pattern

        We are only supporting MaxLength for now, and even then, always generating string of maxLength Char always
        """

        return {
            "maximum": config.get(constants.MAX_LENGTH, 100)    # Arbitrarily set max length
        }

    def get_string(self, config):
        return self.get_enum(config) or self.fake.text(max_nb_chars=self.get_options(config)["maximum"])

    def random_date_time(self, config):
        # Date time between 30 years in past to 30 years in future
        return self.fake.date_time_between(end_date='+30y', tzinfo=timezone.utc)

    def get_date(self, config):
        return self.random_date_time(config).strftime("%Y-%m-%d")

    def get_datetime(self, config):
        return self.random_date_time(config).isoformat()

    def get_password(self, config):
        return self.get_enum(config) or self.fake.password(length=self.get_options(config)["maximum"])

    def get_base64(self, config):
        return base64.b64encode(self.get_string(config))

    def get_binary(self, config):
        return self.get_enum(config) or self.fake.binary(length=self.get_options(config)["maximum"])

    def get_email(self, config):
        return self.get_enum(config) or self.fake.free_email()

    def get_uuid(self, config):
        return self.fake.uuid4()

    def get_boolean(self, config):
        return self.fake.boolean()

    def get_array(self, config):

        item_config = config.get(constants.ITEMS)

        if not item_config:
            raise exceptions.ImproperSwaggerException("Items should be defined for Array type - {}".format(config))

        fake_func = self.get_fake_mapper(item_config)

        min_items = config.get(constants.MIN_ITEMS, 0)
        max_items = config.get(constants.MAX_ITEMS, max(10, min_items+1))

        item_length = random.randint(min_items, max_items)

        fake_items = [fake_func(self, item_config) for _ in range(item_length)]

        is_unique = config.get(constants.UNIQUE_ITEMS, False)

        if is_unique:
            fake_items = set(fake_items)

            # If due to de-duplication, our array count decreases and is less than what is required
            while len(fake_items) < min_items:
                fake_items.add(fake_func(self, item_config))

            fake_items = list(fake_items)

        return fake_items

    def get_object(self, config):

        properties = config.get(constants.PROPERTIES)

        if not properties:
            raise exceptions.ImproperSwaggerException("Properties should be defined for Object - {}".format(config))

        fake_object = {}

        for name, prop_config in properties.items():
            fake_func = self.get_fake_mapper(prop_config)
            if fake_func:
                fake_object[name] = fake_func(self, prop_config)

        return fake_object

    FAKE_MAP = {
        # (Type, format) --> function. None should match to no format. any accepts any format at all
        (constants.INTEGER, None): get_integer,
        (constants.INTEGER, "$any"): get_integer,
        (constants.NUMBER, None): get_float,
        (constants.NUMBER, "$any"): get_float,
        (constants.STRING, None): get_string,
        (constants.STRING, constants.DATE): get_date,
        (constants.STRING, constants.DATE_TIME): get_datetime,
        (constants.STRING, constants.PASSWORD): get_password,
        (constants.STRING, constants.BYTE): get_base64,
        (constants.STRING, constants.EMAIL): get_email,
        (constants.STRING, constants.UUID): get_uuid,
        (constants.BOOLEAN, None): get_boolean,
        (constants.ARRAY, None): get_array,
        (constants.OBJECT, None): get_object
    }


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
