from atlas.modules.commands.base import BaseCommand
from atlas.modules.resource_data_generator.generators import ResourceMap


class Generate(BaseCommand):
    help = "Fetch Data as per Resource map, and create a cache of resources"

    def handle(self, **options):
        res_map = ResourceMap()
        res_map.parse()
