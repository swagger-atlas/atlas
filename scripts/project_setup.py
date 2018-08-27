import os
from pathlib import Path

from scripts import utils
from settings.conf import settings


class Setup:

    def __init__(self):
        self.path = None

    def setup(self):
        self.path = utils.get_project_path()
        self.create_folder(settings.INPUT_FOLDER)
        self.create_folder(settings.OUTPUT_FOLDER)
        self.touch("__init__.py")
        root_path = self.path

        self.path = os.path.join(root_path, settings.OUTPUT_FOLDER)
        self.create_folder(settings.RESOURCES_FOLDER)
        self.touch("__init__.py")

        self.path = os.path.join(root_path, settings.INPUT_FOLDER)
        self.touch("__init__.py")

    def create_folder(self, folder_name):

        folder = os.path.join(self.path, folder_name)

        if not os.path.exists(folder):
            os.makedirs(folder)     # Create all folders and files in the path in nested fashion

    def touch(self, file_name):
        path = os.path.join(self.path, file_name)
        Path(path).touch()


if __name__ == "__main__":
    Setup().setup()
