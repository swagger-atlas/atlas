import os
import subprocess

from atlas.modules.commands.base import BaseCommand, CommandError
from atlas.conf import settings


class LoadTestCommand(BaseCommand):
    """
    Creates an Atlas Application
    """

    help = "Runs Load Test for your application"

    VALID_RUNNERS = {"artillery"}

    def add_arguments(self, parser):
        parser.add_argument(
            "runner_type",
            nargs='?',  # This will make sure that we can pick argument from default or command line
            default="artillery",
            help=f"Valid load test runners are: {self.VALID_RUNNERS}"
        )

    def handle(self, **options):
        runner = options.pop("runner_type")

        if runner == "artillery":
            self.artillery_runner()
        else:
            raise CommandError(f"Invalid Load Test Runner. Valid runners are: {self.VALID_RUNNERS}")

    @staticmethod
    def artillery_runner():
        """
        Wrapper for Artillery Load Test run

        Artillery Run reference:
            https://artillery.io/docs/cli-reference/
            For artillery run, there is no quick way to change number of users
            It is only done by changing complete phase configuration
        """

        file_path = os.path.join(settings.DIST_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_YAML)

        # Print Grafana message at start of load test
        print(grafana_message)

        command = f"artillery run {file_path}"

        # https://docs.python.org/3/library/os.html#os.system
        # subprocess is preferred over os.system
        # https://docs.python.org/3/library/subprocess.html#subprocess.run
        subprocess.run(command.split())

        # Print Grafana message once test has been completed
        print(grafana_message)


grafana_message = """
Running Artillery Load Test. You can see results in real time in Grafana dashboard
Grafana dashboard is available at http://localhost:4000/dashboards (if you followed docker setup)
Default Credentials are: admin/admin
You should see `Artillery Graphs` dashboard.
"""
