from atlas.modules.commands.base import BaseCommand


class TransformerBaseCommand(BaseCommand):
    """
    Base class for commands which require type of transformer as input
    """

    VALID_CONVERTERS = ""

    def add_arguments(self, parser):
        parser.add_argument(
            "type",
            nargs='?',      # This will make sure that we can pick argument from default or command line
            default="artillery",
            help=f"Valid build/dist types are: {self.VALID_CONVERTERS}"
        )

    def handle(self, **options):
        raise NotImplementedError
