from atlas.modules.commands.base import CommandError
from atlas.modules.transformer.commands.base import TransformerBaseCommand
from atlas.modules.transformer.artillery.setup import ArtillerySetup


VALID_TYPES = {"artillery"}


class Setup(TransformerBaseCommand):
    VALID_CONVERTERS = ", ".join(VALID_TYPES)
    help = "Setup the configuration for a specific type"

    def handle(self, **options):
        load_conf_type = options.pop("type")

        if load_conf_type == "artillery":
            self.artillery_setup()
        else:
            raise CommandError("Invalid Load Testing Type. Valid types are: {}".format(self.VALID_CONVERTERS))

    @staticmethod
    def artillery_setup():
        setup = ArtillerySetup()
        setup.setup()
