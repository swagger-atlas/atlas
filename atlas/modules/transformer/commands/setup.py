from atlas.modules.commands.base import BaseCommand, CommandError
from atlas.modules.transformer.k6.setup import K6Setup


VALID_TYPES = {"k6"}


class Setup(BaseCommand):
    VALID_CONVERTERS = ", ".join(VALID_TYPES)
    help = "Setup the configuration for a specific type"

    def add_arguments(self, parser):
        parser.add_argument("type", help="Load Tester Type which should be used. Valid types: {}".format(
            self.VALID_CONVERTERS
        ))

    def handle(self, **options):
        load_conf_type = options.pop("type")

        if load_conf_type == "k6":
            self.k6_setup()
        else:
            raise CommandError("Invalid Load Testing Type. Valid types are: {}".format(self.VALID_CONVERTERS))

    @staticmethod
    def k6_setup():
        setup = K6Setup()
        setup.setup()
