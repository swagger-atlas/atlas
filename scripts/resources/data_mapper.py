import base64
from datetime import timezone
import random

from faker import Faker

from scripts import (
    constants as swagger_constants,
    exceptions
)

# This is arbitrary limit. Test cases should not break with change of this limit.
# Parameters which are sensitive to this should define their own min/max limits
LIMIT = 10 ** 6


class FakeData:

    def __init__(self):
        self.fake = Faker()

    def get_fake_mapper(self, config):
        item_type = config.get(swagger_constants.TYPE)

        # TODO: Reference handling
        if not item_type:
            raise exceptions.ImproperSwaggerException("Item type must be defined")

        item_format = config.get(swagger_constants.FORMAT)

        fake_func = self.FAKE_MAP.get((item_type, item_format), None)

        # If it did not match, try to match any format
        if not fake_func:
            fake_func = self.FAKE_MAP.get((item_type, "$any"), None)

        return fake_func

    @staticmethod
    def get_range(config):
        minimum = config.get(swagger_constants.MINIMUM, -LIMIT)
        maximum = config.get(swagger_constants.MAXIMUM, LIMIT)

        if config.get(swagger_constants.MIN_EXCLUDE, False):
            minimum += 1

        if config.get(swagger_constants.MAX_EXCLUDE, False):
            maximum -= 1

        if minimum > maximum:
            raise exceptions.ImproperSwaggerException("Minimum cannot be lower than maximum")

        return minimum, maximum

    def get_integer(self, config):
        return random.randint(*self.get_range(config)) * config.get(swagger_constants.MULTIPLE_OF, 1)

    def get_float(self, config):
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
            "maximum": config.get(swagger_constants.MAX_LENGTH, 100)    # Arbitrarily set max length
        }

    def get_string(self, config):
        options = self.get_options(config)
        return self.fake.text(max_nb_chars=options["maximum"])

    def random_date_time(self, config):
        # Date time between 30 years in past to 30 years in future
        return self.fake.date_time_between(end_date='+30y', tzinfo=timezone.utc)

    def get_date(self, config):
        return self.random_date_time(config).strftime("%Y-%m-%d")

    def get_datetime(self, config):
        return self.random_date_time(config).isoformat()

    def get_password(self, config):
        options = self.get_options(config)
        return self.fake.password(length=options["maximum"])

    def get_base64(self, config):
        return base64.b64encode(self.get_string(config))

    def get_binary(self, config):
        options = self.get_options(config)
        return self.fake.binary(length=options["maximum"])

    def get_email(self, config):
        return self.fake.free_email()

    def get_uuid(self, config):
        return self.fake.uuid4()

    def get_boolean(self, config):
        return self.fake.boolean()

    def get_array(self, config):

        item_config = config.get(swagger_constants.ITEMS)

        if not item_config:
            raise exceptions.ImproperSwaggerException("Items should be defined for Array type - {}".format(config))

        fake_func = self.get_fake_mapper(item_config)

        min_items = config.get(swagger_constants.MIN_ITEMS, 0)
        max_items = config.get(swagger_constants.MAX_ITEMS, max(10, min_items+1))

        item_length = random.randint(min_items, max_items)

        fake_items = [fake_func(item_config) for _ in range(item_length)]

        is_unique = config.get(swagger_constants.UNIQUE_ITEMS, False)

        if is_unique:
            fake_items = set(fake_items)

            # If due to de-duplication, our array count decreases and is less than what is required
            while len(fake_items) < min_items:
                fake_items.add(fake_func(item_config))

            fake_items = list(fake_items)

        return fake_items

    def get_object(self, config):

        properties = config.get(swagger_constants.PROPERTIES)

        if not properties:
            raise exceptions.ImproperSwaggerException("Properties should be defined for Object - {}".format(config))

        fake_object = {}

        for name, config in properties.items():
            fake_object[name] = self.get_fake_mapper(config)(config)

        return fake_object

    FAKE_MAP = {
        # (Type, format) --> function. None should match to no format. any accepts any format at all
        (swagger_constants.INTEGER, None): get_integer,
        (swagger_constants.INTEGER, "$any"): get_integer,
        (swagger_constants.NUMBER, None): get_float,
        (swagger_constants.NUMBER, "$any"): get_float,
        (swagger_constants.STRING, None): get_string,
        (swagger_constants.STRING, swagger_constants.DATE): get_date,
        (swagger_constants.STRING, swagger_constants.DATE_TIME): get_datetime,
        (swagger_constants.STRING, swagger_constants.PASSWORD): get_password,
        (swagger_constants.STRING, swagger_constants.BYTE): get_base64,
        (swagger_constants.STRING, swagger_constants.EMAIL): get_email,
        (swagger_constants.STRING, swagger_constants.UUID): get_uuid,
        (swagger_constants.BOOLEAN, None): get_boolean,
        (swagger_constants.ARRAY, None): get_array,
        (swagger_constants.OBJECT, None): get_object
    }
