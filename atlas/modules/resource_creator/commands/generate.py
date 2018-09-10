from atlas.modules.commands.base import BaseCommand
from atlas.modules.resource_creator.creators import AutoGenerator


class Generate(BaseCommand):

    help = "Auto generate resources from Swagger file and update Res Mapping and Swagger File"

    def handle(self, **options):
        gen = AutoGenerator()
        gen.parse()
        gen.update()
