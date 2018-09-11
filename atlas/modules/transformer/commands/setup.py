from atlas.modules.commands.base import CommandError
from atlas.modules.transformer.commands.base import TransformerBaseCommand
from atlas.modules.transformer.k6.setup import K6Setup


VALID_TYPES = {"k6"}


class Setup(TransformerBaseCommand):
    VALID_CONVERTERS = ", ".join(VALID_TYPES)
    help = "Setup the configuration for a specific type"

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
