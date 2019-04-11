from importlib import import_module
import os
import shutil

from atlas.modules.commands.base import BaseCommand, CommandError
from atlas.modules.commands.utils import setup_artillery
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
            overwrite = input(f"{project_name} directory already exists! Overwrite (y/N) ")
            if overwrite.lower() == "y":
                print(f"Removing existing {project_name}")
                shutil.rmtree(target)
            else:
                print("Aborting!")
                return

        print(f"Creating {project_name}...")
        shutil.copytree(os.path.join(settings.BASE_DIR, "atlas", settings.APP_TEMPLATE_DIRECTORY), target)

        print("\nProject successfully created\n")

        if options.get("auto_setup", "") == "artillery":
            setup_artillery(target)

        print(success_message)

    @staticmethod
    def validate_name(name):
        # If it's not a valid directory name.
        if not name.isidentifier():
            raise CommandError(
                f"{name} is not a valid project name. Please make sure the name is a valid identifier."
            )


success_message = """
Congratulation, your project is successfully created! Follow these steps to configure your load test:
1. Switch to project directory
2. Run docker compose to install influxdb and grafana - `docker-compose -f docker/docker-compose.yml up`
3. In the conf/ folder, configure conf.py, swagger.yaml, and profiles.yaml file
4. Change settings.py as necessary
5. Run `atlas dist`
"""
