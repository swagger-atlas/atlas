from atlas.modules.commands.base import CommandError
from atlas.modules.commands.utils import add_bool_arg
from atlas.modules.resource_data_generator.commands import generate as fetch_data
from atlas.modules.resource_creator.commands import generate as create_resource
from atlas.modules.transformer.commands.base import TransformerBaseCommand
from atlas.modules.transformer.artillery.dist import ArtilleryDist
from atlas.modules.transformer.commands import converter, setup


VALID_TYPES = {"artillery"}


class Dist(TransformerBaseCommand):
    VALID_CONVERTERS = ", ".join(VALID_TYPES)
    help = "Distribute the build. This distribution can be run stand-alone or directly"

    def add_arguments(self, parser):
        super(Dist, self).add_arguments(parser)

        add_bool_arg(parser, "setup", default=True)
        add_bool_arg(parser, "detect_resources", default=True)
        add_bool_arg(parser, "fetch_data", default=True)

    def handle(self, **options):
        load_conf_type = options.pop("type")

        if load_conf_type == "artillery":
            self.artillery_pipeline(**options)
        else:
            raise CommandError("Invalid Load Testing Type. Valid types are: {}".format(self.VALID_CONVERTERS))

    @staticmethod
    def artillery_dist():
        dist = ArtilleryDist()
        dist.start()

    def artillery_pipeline(self, **options):

        # Create Data Types and then fetch it
        if options.get("detect_resources"):
            print("Resource Detection Started...")
            create_resource.Generate().handle()

        if options.get("fetch_data"):
            print("Fetching Data from database and updating caches...")
            fetch_data.Generate().handle()

        # Setup the Artillery Files
        if options.get("setup"):
            print("Converting Settings/Constants to JS Libraries")
            setup.Setup().handle(type="artillery")

        # Build the Swagger to Artillery Files
        print("Converting your Swagger file to Artillery Load Test...")
        converter.Converter().handle(type="artillery")

        # Now package it for distribution
        print("Preparing your distribution package")
        self.artillery_dist()

        print("Successfully finished. \n\n"
              "You can start the test on local by `artillery run dist/artillery/artillery.yaml`\n"
              "If needed, you can adjust duration and user-spawn rate in dist/artillery.yaml - in config/phases\n")
