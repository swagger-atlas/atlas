import os
import shutil

from atlas.modules.commands.base import BaseCommand, CommandError
from atlas.conf import settings

VALID_EXAMPLES = {"petstore"}


class ExampleProjectCommand(BaseCommand):
    """
    Creates an Atlas Application Example
    """

    help = "Creates an example project based on ATLAS"

    def add_arguments(self, parser):
        parser.add_argument("name", help=f"Name of the example. Valid examples are {', '.join(VALID_EXAMPLES)}")

    def handle(self, **options):
        """
        :param options: (dict)
            - name: Name of Example Project to create
        """

        project_name = options.pop("name")
        self.validate_name(project_name)

        target = os.path.join(os.getcwd(), project_name)
        if os.path.exists(target):
            raise CommandError("{} directory already exists! Please select another location".format(project_name))

        shutil.copytree(os.path.join(settings.BASE_DIR, "atlas", settings.EXAMPLE_DIRECTORY, project_name), target)

    @staticmethod
    def validate_name(name):
        # If it's not a valid directory name.
        if name not in VALID_EXAMPLES:
            raise CommandError(
                f"{name} is not a valid example name. Valid examples are:  {', '.join(VALID_EXAMPLES)}"
            )
