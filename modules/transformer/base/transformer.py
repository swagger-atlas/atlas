from io import open
import os

from modules import utils
from settings.conf import settings


class FileConfig:

    OUT_FILE = None

    def __init__(self, task_set, specs_file=None):
        self.task_set = task_set
        self.spec_file = specs_file or settings.SWAGGER_FILE

    @staticmethod
    def get_imports():
        raise NotImplementedError

    @staticmethod
    def get_global_vars():
        return ""

    def convert(self):
        file_components = ["{imports}", "{global_vars}", "{task_set}"]
        return "\n\n\n".join(file_components).format(**utils.StringDict(
            imports=self.get_imports(),
            global_vars=self.get_global_vars(),
            task_set=self.task_set.convert(width=1)
        ))

    def write_to_file(self, file_name=None):
        file_name = file_name or self.OUT_FILE
        _file = os.path.join(utils.get_project_path(), settings.OUTPUT_FOLDER, file_name)

        with open(_file, 'w') as write_file:
            write_file.write(self.convert() + "\n")  # Append EOF New line
