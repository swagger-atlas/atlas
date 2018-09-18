from atlas.modules.commands.base import BaseCommand


class TransformerBaseCommand(BaseCommand):

    VALID_CONVERTERS = ""

    def add_arguments(self, parser):
        parser.add_argument("type", help="Load Tester Type which should be used. Valid types: {}".format(
            self.VALID_CONVERTERS
        ))

    def handle(self, **options):
        raise NotImplementedError
