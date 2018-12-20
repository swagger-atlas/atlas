from atlas.modules.commands.base import BaseCommand
from atlas.modules.helpers import open_api_reader, swagger


class Validate(BaseCommand):

    help = "Validates the Swagger File"

    def handle(self, **options):
        specs = open_api_reader.SpecsFile().inp_file_load()
        validator = swagger.Swagger(specs)
        validator.validate()
