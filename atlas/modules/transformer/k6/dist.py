from collections import namedtuple
import os
import shutil
import subprocess

from atlas.modules import utils, project_setup
from atlas.conf import settings


PySed = namedtuple('py_sed_tuple', ['pattern', 'replace_text'])


class K6Dist(project_setup.Setup):

    def start(self):
        self.path = utils.get_project_path()
        self.create_folder(settings.DIST_FOLDER)

        self.copy_files()
        self.copy_folders()

        self.change_project_imports()
        self.change_vendor_imports()

    def copy_files(self):

        source_files = [
            os.path.join(self.path, settings.OUTPUT_FOLDER, settings.ARTILLERY_FILE),
            os.path.join(self.path, settings.OUTPUT_FOLDER, settings.ARTILLERY_YAML),
            os.path.join(self.path, settings.OUTPUT_FOLDER, settings.K6_PROFILES),
            os.path.join(self.path, settings.OUTPUT_FOLDER, settings.K6_RESOURCES),
            os.path.join(self.path, settings.INPUT_FOLDER, settings.K6_HOOK_FILE),
            os.path.join(settings.BASE_DIR, "atlas", "modules", "data_provider", "k6", "providers.js"),
            os.path.join(settings.BASE_DIR, "atlas", "modules", "data_provider", "k6", "hookSetup.js"),
            os.path.join(settings.BASE_DIR, "atlas", "modules", "data_provider", "k6", "profile.js")
        ]

        for _file in source_files:
            shutil.copy(_file, os.path.join(self.path, settings.DIST_FOLDER))

    def copy_folders(self):

        CopyFolder = namedtuple("copy_folder", ["source_path", "destination_path"])

        folders = [
            CopyFolder(os.path.join(self.path, "js_libs"), os.path.join(self.path, settings.DIST_FOLDER, "js_libs"))
        ]

        # Remove destination folder(s) if already exists
        for _folder in folders:
            if os.path.exists(_folder.destination_path):
                shutil.rmtree(_folder.destination_path)

        # Now copy all source folders to destination folders
        for _folder in folders:
            shutil.copytree(_folder.source_path, _folder.destination_path)

    @staticmethod
    def change_project_imports():
        """
        Change Absolute Paths of Project files to relative paths
        """

        # No one else should be accessing these files
        source_files = [
            os.path.join(utils.get_project_path(), settings.DIST_FOLDER, settings.ARTILLERY_FILE)
        ]

        import_files = [settings.K6_HOOK_FILE, "providers.js"]

        sed_commands = []

        # Create a sed command to replace imports
        # We actually use PYSED library than bash sed to ensure wider OS compatibility
        for _file in import_files:
            sed_commands.append(PySed(f"(^import .* from )'.*{_file}'", f"\\1'./{_file}'"))

        for _file in source_files:
            for sed_command in sed_commands:
                subprocess.call(["pysed", "-r", sed_command.pattern, sed_command.replace_text, _file, "--write"])

    @staticmethod
    def change_vendor_imports():
        """
        Change Absolute Paths of Vendor files to relative paths
        """

        # No one else should be accessing these files
        source_files = [
            os.path.join(utils.get_project_path(), settings.DIST_FOLDER, settings.K6_HOOK_FILE),
            os.path.join(utils.get_project_path(), settings.DIST_FOLDER, "providers.js"),
            os.path.join(utils.get_project_path(), settings.DIST_FOLDER, "hookSetup.js"),
            os.path.join(utils.get_project_path(), settings.DIST_FOLDER, "profile.js"),
            os.path.join(utils.get_project_path(), settings.DIST_FOLDER, settings.ARTILLERY_FILE),
            os.path.join(utils.get_project_path(), settings.DIST_FOLDER, "resources.js"),
        ]

        sed_command = PySed(pattern=f"(^import .* from )'js_libs(.*)'", replace_text=f"\\1'./js_libs\\2'")

        for _file in source_files:
            subprocess.call(["pysed", "-r", sed_command.pattern, sed_command.replace_text, _file, "--write"])
