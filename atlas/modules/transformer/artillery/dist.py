from collections import namedtuple
import os
import shutil

from atlas.modules import utils
from atlas.conf import settings


PySed = namedtuple('py_sed_tuple', ['pattern', 'replace_text'])


class ArtilleryDist:
    """
    Creates a package for artillery

    1. Creates required folders
    2. Copy files from BUILD folder to DIST folder
    3. Copy internal files to DIST folder
    """

    def __init__(self):
        self.path = None

    def start(self):
        self.path = utils.get_project_path()
        self.create_folder(settings.DIST_FOLDER)
        self.create_folder(settings.ARTILLERY_FOLDER, os.path.join(self.path, settings.DIST_FOLDER))

        self.copy_folders()
        self.copy_files()

    def copy_files(self):

        source_path = os.path.join(settings.BASE_DIR, "atlas", "modules", "data_provider", "artillery")

        # Some files are dynamically generated during build time,
        #   and we would use them instead of static templates provided in the folder
        # Rest of templates are copied over as it is
        source_files = [
            os.path.join(source_path, file) for file in os.listdir(source_path)
            if file not in {"constants.js", "settings.js", settings.ARTILLERY_RESOURCES}
        ]
        d_path = os.path.join(self.path, settings.DIST_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_LIB_FOLDER)

        for _file in source_files:
            if os.path.isfile(_file):
                shutil.copy(_file, d_path)

        artillery_source_files = [
            os.path.join(self.path, settings.INPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_HOOK_FILE),
            os.path.join(self.path, settings.OUTPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_FILE),
            os.path.join(self.path, settings.OUTPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_YAML),
        ]

        for _file in artillery_source_files:
            shutil.copy(_file, os.path.join(self.path, settings.DIST_FOLDER, settings.ARTILLERY_FOLDER))

        base_files = [
            os.path.join(self.path, settings.OUTPUT_FOLDER, settings.SWAGGER_FILE)
        ]

        for _file in base_files:
            shutil.copy(_file, settings.DIST_FOLDER)

    def copy_folders(self):

        CopyFolder = namedtuple("copy_folder", ["source_path", "destination_path"])

        folders = [
            CopyFolder(
                os.path.join(
                    self.path, settings.OUTPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_LIB_FOLDER
                ),
                os.path.join(self.path, settings.DIST_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_LIB_FOLDER)
            ),
            CopyFolder(
                os.path.join(settings.BASE_DIR, "atlas", "modules", "data_provider", "sample-files"),
                os.path.join(self.path, settings.DIST_FOLDER, settings.DUMMY_FILES_FOLDER)
            )
        ]

        # Remove destination folder(s) if already exists
        for _folder in folders:
            if os.path.exists(_folder.destination_path):
                shutil.rmtree(_folder.destination_path)

        # Now copy all source folders to destination folders
        for _folder in folders:
            shutil.copytree(_folder.source_path, _folder.destination_path)

    def create_folder(self, folder_name, path=None):

        path = path or self.path
        folder = os.path.join(path, folder_name)

        if not os.path.exists(folder):
            os.makedirs(folder)     # Create all folders and files in the path in nested fashion
