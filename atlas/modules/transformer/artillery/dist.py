from collections import namedtuple
import os
import shutil

from atlas.modules import utils, project_setup
from atlas.conf import settings


PySed = namedtuple('py_sed_tuple', ['pattern', 'replace_text'])


class ArtilleryDist(project_setup.Setup):

    def start(self):
        self.path = utils.get_project_path()
        self.create_folder(settings.DIST_FOLDER)

        self.copy_folders()
        self.copy_files()

    def copy_files(self):

        source_files = [
            os.path.join(self.path, settings.INPUT_FOLDER, settings.ARTILLERY_HOOK_FILE),
            os.path.join(settings.BASE_DIR, "atlas", "modules", "data_provider", "artillery", "providers.js"),
            os.path.join(settings.BASE_DIR, "atlas", "modules", "data_provider", "artillery", "hookSetup.js"),
            os.path.join(settings.BASE_DIR, "atlas", "modules", "data_provider", "artillery", "statsCollector.js"),
        ]

        for _file in source_files:
            shutil.copy(_file, os.path.join(self.path, settings.DIST_FOLDER, settings.ARTILLERY_LIB_FOLDER))

        artillery_source_files = [
            os.path.join(self.path, settings.OUTPUT_FOLDER, settings.ARTILLERY_FILE),
            os.path.join(self.path, settings.OUTPUT_FOLDER, settings.ARTILLERY_YAML),
        ]

        for _file in artillery_source_files:
            shutil.copy(_file, os.path.join(self.path, settings.DIST_FOLDER))

    def copy_folders(self):

        CopyFolder = namedtuple("copy_folder", ["source_path", "destination_path"])

        folders = [
            CopyFolder(os.path.join(self.path, settings.OUTPUT_FOLDER, settings.ARTILLERY_LIB_FOLDER),
                       os.path.join(self.path, settings.DIST_FOLDER, settings.ARTILLERY_LIB_FOLDER))
        ]

        # Remove destination folder(s) if already exists
        for _folder in folders:
            if os.path.exists(_folder.destination_path):
                shutil.rmtree(_folder.destination_path)

        # Now copy all source folders to destination folders
        for _folder in folders:
            shutil.copytree(_folder.source_path, _folder.destination_path)
