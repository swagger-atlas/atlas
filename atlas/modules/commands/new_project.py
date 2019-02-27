from importlib import import_module
import os
import shutil
import subprocess

from atlas.modules.commands.base import BaseCommand, CommandError
from atlas.conf import settings


class StartProjectCommand(BaseCommand):
    """
    Creates an Atlas Application
    """

    help = "Creates a new project based on ATLAS"

    def add_arguments(self, parser):
        parser.add_argument("name", help="Name of the application or project.")
        parser.add_argument(
            "--auto-setup",
            help="Name of Runner for which you want to auto-setup packages",
            default="artillery"
        )

    def handle(self, **options):
        project_name = options.pop("name")
        self.validate_name(project_name)

        # Check that the project_name cannot be imported.
        try:
            import_module(project_name)
        except ImportError:
            pass
        else:
            raise CommandError(
                f"{project_name} conflicts with the name of an existing Python module and "
                "cannot be used as a project name. Please try another name."
            )

        target = os.path.join(os.getcwd(), project_name)
        if os.path.exists(target):
            raise CommandError(f"{project_name} directory already exists! Aborting")

        shutil.copytree(os.path.join(settings.BASE_DIR, settings.APP_TEMPLATE_DIRECTORY), target)

        print("\nProject successfully created\n")

        if options.get("auto_setup", "") == "artillery":
            self.setup_artillery(target, project_name)

    @staticmethod
    def setup_artillery(target, project_name):
        """
        Setup packages for artillery
        """

        os.chdir(target)

        print("Setting up packages for Artillery\n")

        subprocess.run(["npm", "install", "-g", "artillery"])
        subprocess.run(["npm", "install"])

        print(
            f"You should now switch to {project_name} (cd {project_name})."
            f" In the `conf` directory, add your swagger file and profiles configuration"
        )

    @staticmethod
    def validate_name(name):
        # If it's not a valid directory name.
        if not name.isidentifier():
            raise CommandError(
                f"{name} is not a valid project name. Please make sure the name is a valid identifier."
            )
