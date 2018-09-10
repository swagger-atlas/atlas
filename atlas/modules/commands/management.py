from argparse import ArgumentParser
import importlib
import sys

from atlas.modules.commands.base import CommandError, handle_default_options


COMMANDS = {
    "newproject": 'atlas.modules.commands.new_project.StartProjectCommand',
}


class CommandUtility:

    VALID_COMMANDS = ", ".join(COMMANDS.keys())

    def __init__(self, args=None):
        args = args or sys.argv[:]

        # First argument would always be atlas or manage.py, i.e the calling interface
        if len(args) < 2:
            CommandError.print_to_err("Name of command missing. Valid commands are - {}".format(self.VALID_COMMANDS))

        self.command = args[1]
        self.args = args

    def execute(self):
        command_path = self.fetch_command()

        if not command_path:
            CommandError.print_to_err("Invalid command. Valid commands are - {}".format(self.VALID_COMMANDS))

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
