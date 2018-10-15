from atlas.modules.commands.base import CommandError
from atlas.modules.commands.utils import add_bool_arg
from atlas.modules.resource_data_generator.commands import generate as fetch_data
from atlas.modules.resource_creator.commands import generate as create_resource
from atlas.modules.transformer.commands.base import TransformerBaseCommand
from atlas.modules.transformer.k6.dist import K6Dist
from atlas.modules.transformer.commands import converter, setup


VALID_TYPES = {"k6"}


class Dist(TransformerBaseCommand):
    VALID_CONVERTERS = ", ".join(VALID_TYPES)
    help = "Distribute the build. This distribution can be run stand-alone or directly"

    def add_arguments(self, parser):
        super(Dist, self).add_arguments(parser)

        add_bool_arg(parser, "setup", default=True)
        add_bool_arg(parser, "detect-resources", default=True)
        add_bool_arg(parser, "fetch-data", default=True)

    def handle(self, **options):
        load_conf_type = options.pop("type")

        if load_conf_type == "k6":
            self.k6_pipeline(**options)
        else:
            raise CommandError("Invalid Load Testing Type. Valid types are: {}".format(self.VALID_CONVERTERS))

    @staticmethod
    def k6_dist():
        dist = K6Dist()
        dist.start()

    def k6_pipeline(self, **options):

        # Create Data Types and then fetch it
        if options.get("detect-resources"):
            print("Resource Detection Started...")
            create_resource.Generate().handle()

        if options.get("fetch-data"):
            print("Updating Cached Databases...")
            fetch_data.Generate().handle()

        # Setup the K6 Files
        if options.get("setup"):
            print("Setting up JS Libraries")
            setup.Setup().handle(type="k6")

        # Build the Swagger to K6 Files
        print("Converting your Swagger file to K6 Load Test...")
        converter.Converter().handle(type="k6")

        # Now package it for distribution
        print("Preparing your distribution package")
        self.k6_dist()

        print("Successfully finished. \n\nYou can start the test on local by `k6 run dist/k6.js`\n")
