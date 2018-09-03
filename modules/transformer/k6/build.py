import os
import subprocess

from modules import utils, project_setup
from settings.conf import settings


class K6Build(project_setup.Setup):

    def build(self):
        self.path = utils.get_project_path()
        self.create_folder(settings.BUILD_FOLDER)

        self.copy_files()
        self.copy_folders()

        self.change_project_imports()
        self.change_vendor_imports()

    def copy_files(self):

        source_files = [
            os.path.join(self.path, settings.OUTPUT_FOLDER, settings.K6_FILE),
            os.path.join(self.path, settings.INPUT_FOLDER, settings.PROFILES_FILE),
            os.path.join(self.path, settings.INPUT_FOLDER, settings.K6_HOOK_FILE),
            os.path.join(settings.BASE_DIR, "modules", "data_provider", "k6", "providers.js")
        ]

        for _file in source_files:
            subprocess.call("cp {} {}".format(_file, os.path.join(self.path, settings.BUILD_FOLDER)).split())

    def copy_folders(self):

        source_folders = [
            os.path.join(self.path, settings.OUTPUT_FOLDER, settings.RESOURCES_FOLDER),
            os.path.join(settings.BASE_DIR, "js_libs")
        ]

        for _folder in source_folders:
            subprocess.call("cp -R {} {}".format(_folder, os.path.join(self.path, settings.BUILD_FOLDER)).split())

    @staticmethod
    def change_project_imports():
        """
        Change Absolute Paths of Project files to relative paths
        """

        # No one else should be accessing these files
        source_files = [
            os.path.join(utils.get_project_path(), settings.BUILD_FOLDER, settings.K6_FILE)
        ]

        import_files = [settings.K6_HOOK_FILE, "providers.js"]

        sed_commands = []

        for _file in import_files:
            sed_commands.append(
                "s:(^import .* from )'.*{file_name}':\\1'./{file_name}':".format(file_name=_file)
            )

        for _file in source_files:
            for sed_command in sed_commands:
                subprocess.call(["sed", "-Ei", sed_command, _file])

    @staticmethod
    def change_vendor_imports():
        """
        Change Absolute Paths of Vendor files to relative paths
        """

        # No one else should be accessing these files
        source_files = [
            os.path.join(utils.get_project_path(), settings.BUILD_FOLDER, settings.K6_HOOK_FILE),
            os.path.join(utils.get_project_path(), settings.BUILD_FOLDER, "providers.js"),
            os.path.join(utils.get_project_path(), settings.BUILD_FOLDER, settings.K6_FILE),
        ]

        sed_command = "s:(^import .* from )'js_libs(.*)':\\1'./js_libs\\2':"

        for _file in source_files:
            subprocess.call(["sed", "-Ei", sed_command, _file])


if __name__ == "__main__":
    build = K6Build()
    build.build()
