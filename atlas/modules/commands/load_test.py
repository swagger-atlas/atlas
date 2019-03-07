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

        parser.add_argument(
            "--rate",
            nargs="?",
            help="Rate at which users are added to system. Will over-ride conf settings"
        )

        parser.add_argument(
            "--duration",
            nargs="?",
            help="Duration for which this load test should run. Will over-ride conf settings"
        )

    def handle(self, **options):
        runner = options.pop("runner_type")

        if runner == "artillery":
            self.artillery_runner(**options)
        else:
            raise CommandError(f"Invalid Load Test Runner. Valid runners are: {self.VALID_RUNNERS}")

    @staticmethod
    def artillery_runner(**options):
        """
        Wrapper for Artillery Load Test run

        Artillery Run reference:
            https://artillery.io/docs/cli-reference/
            For artillery run, there is no quick way to change number of users
            It is only done by changing complete phase configuration
        """

        file_path = os.path.join(settings.DIST_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_YAML)

        # Print Grafana message at start of load test
        print(load_test_start_message)

        # Construct Options for Load
        rate = options.get("rate")
        duration = options.get("duration")

        if rate or duration:
            # Do not add spaces for formatting, as we split by space later in the command
            config = '{{"config":{{"phases":[{{"duration":{duration},"arrivalRate":{rate}}}]}}}}'.format(
                duration=duration or settings.DURATION, rate=rate or settings.SPAWN_RATE
            )
            command = f"artillery run --overrides {config} {file_path}"
        else:
            command = f"artillery run {file_path}"

        # https://docs.python.org/3/library/os.html#os.system
        # subprocess is preferred over os.system
        # https://docs.python.org/3/library/subprocess.html#subprocess.run
        subprocess.run(command.split())

        # Print Grafana message once test has been completed
        print(load_test_end_message)


grafana_message = """
Grafana dashboard is available at http://localhost:4000/dashboards (if you followed docker setup)
Default Credentials are: admin/admin
You should be able to see `Artillery Graphs` dashboard, where you can see the results
"""


load_test_start_message = """
Running Artillery Load Test. You can see results in real time in Grafana dashboard""" + grafana_message

load_test_end_message = """
Artillery Load test has finished. You can find results in Grafana dashboard""" + grafana_message
