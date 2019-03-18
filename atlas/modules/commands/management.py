from argparse import ArgumentParser
import importlib
import subprocess
import sys

from atlas.modules.commands.base import CommandError, handle_default_options


# List of all commands with the mapping of the class which implements them
COMMANDS = {
    "newproject": 'atlas.modules.commands.new_project.StartProjectCommand',
    "example": 'atlas.modules.commands.example.ExampleProjectCommand',
    "build": 'atlas.modules.commands.build.BuildProjectCommand',
    "transform": "atlas.modules.transformer.commands.converter.Converter",
    "validate": "atlas.modules.helpers.commands.validate.Validate",
    "generate_routes": "atlas.modules.helpers.commands.generate_routes.Generator",
    "detect_resources": "atlas.modules.resource_creator.commands.generate.Generate",
    "fetch_data": "atlas.modules.resource_data_generator.commands.generate.Generate",
    "setup": "atlas.modules.transformer.commands.setup.Setup",
    "dist": "atlas.modules.transformer.commands.dist.Dist",
    "order": "atlas.modules.transformer.commands.order.Order",
    "run": "atlas.modules.commands.load_test.LoadTestCommand"
}

# Commands which can be run from anywhere.
# Rest of commands need to be run from folder where manage.py resides in folder directory
GLOBAL_COMMANDS = {"newproject", "example"}

VALID_COMMANDS = ", ".join(COMMANDS.keys())


class CommandUtility:
    """
    Class which
        - takes in command,
        - match it with relevant class which implements it
        - call the class with correct options
    """

    def __init__(self, args=None):
        args = args or sys.argv[:]

        self.command = get_command_name(args)
        self.args = args

    def execute(self):
        command_path = self.fetch_command()

        if not command_path:
            CommandError.print_to_err(f"Invalid command. Valid commands are - {VALID_COMMANDS}")

        parser = ArgumentParser(usage="%(prog)s subcommand [options] [args]", add_help=False)
        parser.add_argument('--pythonpath')
        parser.add_argument('args', nargs='*')  # catch-all

        options = parser.parse_known_args(self.args[2:])[0]
        handle_default_options(options)

        command_class = self.load_command(command_path)

        return command_class.run_from_argv(self.args)

    def fetch_command(self):
        return COMMANDS.get(self.command)

    @staticmethod
    def load_command(command_path):
        """
        Given a string path, return the relevant class
        """
        module_path, class_name = command_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)()


def execute_from_command_line(argv=None):
    """
    Helper function to execute via command line
    """

    argv = argv or sys.argv[:]

    command_name = get_command_name(argv)

    if command_name in GLOBAL_COMMANDS:
        # Global commands are those which can be run from any directory as long as this package is installed
        command = CommandUtility(argv)
        command.execute()
    else:
        # Rest of commands must be run via manage.py interface
        # This interface is necessary since it loads user configuration and settings
        command = ["python", "manage.py"]
        command.extend(argv[1:])

        # It may be a good idea for us to add the check that we can access manage.py before running the command?
        subprocess.run(command)


def get_command_name(args):
    """
    Return name of command which is being run
    """

    # First argument would always be atlas or manage.py, i.e the calling interface
    if len(args) < 2:
        CommandError.print_to_err(f"Name of command missing. Valid commands are - {VALID_COMMANDS}")

    return args[1]
