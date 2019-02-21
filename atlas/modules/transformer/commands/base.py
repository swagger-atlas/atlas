from atlas.modules.commands.base import BaseCommand


class TransformerBaseCommand(BaseCommand):
    """
    Base class for commands which require type of transformer as input
    """

    VALID_CONVERTERS = ""

    def add_arguments(self, parser):
        parser.add_argument("type", help="Load Tester Type which should be used. Valid types: {}".format(
            self.VALID_CONVERTERS
        ))

    def handle(self, **options):
        raise NotImplementedError
