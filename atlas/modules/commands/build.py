import os

from atlas.modules.commands.base import BaseCommand
from atlas.modules.commands.utils import setup_artillery


class BuildProjectCommand(BaseCommand):
    """
    Setup ATLAS Project dependencies
    """

    help = "Installs ATLAS dependencies based on load runner"

    def add_arguments(self, parser):
        parser.add_argument(
            "--auto-setup",
            help="Name of Runner for which you want to auto-build packages",
            default="artillery"
        )

    def handle(self, **options):
        target = os.getcwd()

        if options.get("auto_setup", "") == "artillery":
            setup_artillery(target)

        print("Packages are successfully installed.")
