from atlas.modules.commands.base import BaseCommand
from atlas.modules.helpers import open_api_reader, generate_routes


class Generator(BaseCommand):

    help = "Generates the Routes file for Swagger. This also gives OP_KEY for all routes"

    def handle(self, **options):
        specs = open_api_reader.SpecsFile().inp_file_load()
        generator = generate_routes.GenerateRoutes(specs)
        generator.write_to_routes()
