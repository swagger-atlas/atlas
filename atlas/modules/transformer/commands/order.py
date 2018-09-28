from atlas.modules.commands.base import BaseCommand
from atlas.modules.transformer.ordering import ordering


class Order(BaseCommand):
    help = "Order the Operations as needed. This is provided for debugging purposes"

    def handle(self, **options):
        order = ordering.Ordering()
        order.order()
        return "Ordered Successfully\n"
