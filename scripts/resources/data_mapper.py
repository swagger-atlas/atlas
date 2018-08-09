from abc import ABC, abstractmethod
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


class FakeData(ABC):
    """
    Abstract class for fake data generation
    """

    def __init__(self):
        self.fake = Faker()

    @abstractmethod
    def generate_fake_data(self, config):
        raise NotImplementedError


class NumberData(FakeData, ABC):

    @abstractmethod
    def generate_fake_data(self, config):
        raise NotImplementedError

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


class IntegerData(NumberData):

    def generate_fake_data(self, config):
        return random.randint(*self.get_range(config))*config.get(swagger_constants.MULTIPLE_OF, 1)


class FloatData(NumberData):

    def generate_fake_data(self, config):
        minimum, maximum = self.get_range(config)
        left_side = random.randint(minimum, maximum)
        right_side = round(random.random(), 2)

        final_number = left_side + right_side

        if final_number > maximum:
            final_number = float(maximum)

        if final_number < minimum:
            final_number = float(minimum)

        return final_number


class BaseStringData(FakeData, ABC):

    @abstractmethod
    def generate_fake_data(self, config):
        raise NotImplementedError

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


class StringData(BaseStringData):

    def generate_fake_data(self, config):
        options = self.get_options(config)
        return self.fake.text(max_nb_chars=options["maximum"])


class DateData(BaseStringData):

    def generate_fake_data(self, config):
        return self.fake.date()


class DateTimeDate(BaseStringData):

    def generate_fake_data(self, config):
        return self.fake.iso8601(tzinfo=timezone.utc)


class PasswordData(BaseStringData):

    def generate_fake_data(self, config):
        options = self.get_options(config)
        return self.fake.password(length=options["maximum"])


class Base64Data(StringData):

    def generate_fake_data(self, config):
        return base64.b64encode(super().generate_fake_data(config))


class BinaryData(BaseStringData):

    def generate_fake_data(self, config):
        options = self.get_options(config)
        return self.fake.binary(length=options["maximum"])


class EmailData(BaseStringData):

    def generate_fake_data(self, config):
        return self.fake.free_email()


class UUIDData(BaseStringData):

    def generate_fake_data(self, config):
        return self.fake.uuid4()


class BooleanData(FakeData):

    def generate_fake_data(self, config):
        return self.fake.boolean()
