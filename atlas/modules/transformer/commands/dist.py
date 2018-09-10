from atlas.modules.commands.base import BaseCommand, CommandError
from atlas.modules.transformer.k6.dist import K6Dist


VALID_TYPES = {"k6"}


class Dist(BaseCommand):
    VALID_CONVERTERS = ", ".join(VALID_TYPES)
    help = "Distribute the build. This distribution can be run stand-alone or directly"

    def add_arguments(self, parser):
        parser.add_argument("type", help="Load Tester Type which should be used. Valid types: {}".format(
            self.VALID_CONVERTERS
        ))

    def handle(self, **options):
        load_conf_type = options.pop("type")

        if load_conf_type == "k6":
            self.k6_dist()
        else:
            raise CommandError("Invalid Load Testing Type. Valid types are: {}".format(self.VALID_CONVERTERS))

    @staticmethod
    def k6_dist():
        dist = K6Dist()
        dist.start()
