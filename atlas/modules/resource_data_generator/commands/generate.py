from atlas.modules.commands.base import BaseCommand
from atlas.modules.resource_data_generator.generators import ProfileResourceDataGenerator


class Generate(BaseCommand):
    help = "Fetch Data as per Resource map, and create a cache of resources"

    def handle(self, **options):
        res_map = ProfileResourceDataGenerator()
        res_map.parse()
