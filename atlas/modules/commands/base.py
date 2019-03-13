from argparse import ArgumentParser
import os
import sys


class CommandError(Exception):
    """
    Exception class indicating a problem while executing a management
    command.
    """

    @classmethod
    def print_to_err(cls, err, err_writer=sys.stderr):
        err_writer.write(f"{cls.__name__}: {err}\n")
        sys.exit(1)


def handle_default_options(options):
    """
    Include any default options that all commands should accept here
    so that ManagementUtility can handle them before searching for
    user commands.
    """
    if options.pythonpath:
        sys.path.insert(0, options.pythonpath)


class BaseCommand:
    """
    The base class from which all management commands ultimately
    derive.
    """
    help = ''

    def __init__(self, stdout=None, stderr=None):
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def create_parser(self, program_name, sub_command):
        """
        Create and return the ``ArgumentParser`` which will be used to
        parse the arguments to this command.
        """
        parser = ArgumentParser(
            prog="{} {}".format(os.path.basename(program_name), sub_command),
            description=self.help or None,
        )
        parser.add_argument(
            '--pythonpath',
            help='A directory to add to the Python path, e.g. "/home/projects/my_project".',
        )
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """

    def print_help(self, *args, **kwargs):
        """
        Print the help message for this command, derived from
        ``self.usage()``.
        """
        parser = self.create_parser(*args, **kwargs)
        parser.print_help()

    def run_from_argv(self, argv):
        """
        Set up any environment changes requested (e.g., Python path),
        then run this command. If the command raises a ``CommandError``,
        intercept it and print it sensibly to stderr.
        If the the raised ``Exception`` is not ``CommandError``, raise it.
        """
        parser = self.create_parser(argv[0], argv[1])

        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        handle_default_options(options)
        try:
            self.execute(**cmd_options)
        except CommandError as err:
            CommandError.print_to_err(err, self.stderr)

    def execute(self, **options):
        """
        Try to execute this command
        """

        output = self.handle(**options)
        if output:
            self.stdout.write(output)
        return output

    def handle(self, **options):
        """
        The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError('subclasses of BaseCommand must provide a handle() method')
