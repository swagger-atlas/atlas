from importlib import import_module
import os
import shutil

from modules.commands.base import BaseCommand, CommandError
from settings.conf import settings


class StartProjectCommand(BaseCommand):
    """
    Creates an Atlas Application
    """

    def add_arguments(self, parser):
        parser.add_argument('name', help='Name of the application or project.')

    def handle(self, **options):
        project_name = options.pop('name')
        self.validate_name(project_name)

        # Check that the project_name cannot be imported.
        try:
            import_module(project_name)
        except ImportError:
            pass
        else:
            raise CommandError(
                "{} conflicts with the name of an existing Python module and "
                "cannot be used as a project name. Please try another name.".format(project_name)
            )

        target = os.path.join(os.getcwd(), project_name)
        if os.path.exists(target):
            raise CommandError("{} directory already exists! Aborting".format(project_name))

        shutil.copytree(os.path.join(settings.BASE_DIR, settings.APP_TEMPLATE_DIRECTORY), target)

    @staticmethod
    def validate_name(name):
        # If it's not a valid directory name.
        if not name.isidentifier():
            raise CommandError(
                "{} is not a valid project name. Please make sure the name is "
                "a valid identifier.".format(name)
            )
