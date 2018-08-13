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
    }
