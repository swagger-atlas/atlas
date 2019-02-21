from io import open
import os

import yaml

from atlas.modules import utils
from atlas.conf import settings


RESOURCE_FILE_NAME = "resource_file"


class YAMLReadWriteMixin:
    """
    To read and write YAML files in Project Folder.
    """

    @staticmethod
    def get_project_folder(sub_folder: str = None) -> str:
        """
        Get the base path of folder from where files should be read and/or written to
        :param sub_folder: Sub folder path which should be added to base path
        """

        project_path = utils.get_project_path()

        if sub_folder:
            project_path = os.path.join(project_path, sub_folder)

        return project_path

    def read_file(self, file_name, default_value=None, project_sub_folder=None):
        """
        Safely Read YAML file
        :param file_name: Name of file
        :param default_value: Default value to return in case of any error or empty file
        :param project_sub_folder: Name of folder where file is present
        """

        _file = os.path.join(self.get_project_folder(project_sub_folder), file_name)

        try:
            with open(_file) as file_stream:
                ret_stream = yaml.safe_load(file_stream)
        except FileNotFoundError:
            ret_stream = default_value

        return ret_stream or default_value

    def read_file_from_input(self, *args, **kwargs):
        """
        Read YAML file from INPUT folder.
        Same as read_file, except we add INPUT folder as sub_folder.
        """
        sub_folder = kwargs.pop('project_sub_folder', None)
        sub_folder = os.path.join(settings.INPUT_FOLDER, sub_folder) if sub_folder else settings.INPUT_FOLDER
        return self.read_file(*args, **kwargs, project_sub_folder=sub_folder)

    def read_file_from_output(self, *args, **kwargs):
        """
        Read YAML file from INPUT folder.
        Same as read_file, except we add OUTPUT folder as sub_folder.
        """
        sub_folder = kwargs.pop('project_sub_folder', None)
        sub_folder = os.path.join(settings.OUTPUT_FOLDER, sub_folder) if sub_folder else settings.OUTPUT_FOLDER
        return self.read_file(*args, **kwargs, project_sub_folder=sub_folder)

    def write_file(
            self, file_name, write_data, project_sub_folder=None, append_mode: bool = True, force_write: bool = False
    ):
        """
        Write contents of write_data to YAML file
        :param file_name: Name of file
        :param write_data: Data to be written. We should be able to convert this in YAML
        :param project_sub_folder: Name/Path of folder where you want to write the data
        :param append_mode: If true, add to current file, else, over-write existing contents
        :param force_write: Write the data to file even if write_data is empty
        """

        _path = self.get_project_folder(project_sub_folder)

        if not os.path.exists(_path):
            os.makedirs(_path)

        _file = os.path.join(_path, file_name)

        # If there is no data to write, no point opening a file
        # You can over-write the behaviour by specifying that you want to force write
        if write_data or force_write:
            write_mode = "a" if append_mode else "w"
            with open(_file, write_mode) as file_stream:
                yaml.dump(write_data, file_stream, default_flow_style=False)

    def write_file_to_input(self, *args, **kwargs):
        """
        Write YAML file to INPUT folder.
        Same as write_file, except we add INPUT folder as sub_folder.
        """
        sub_folder = kwargs.pop('project_sub_folder', None)
        sub_folder = os.path.join(settings.INPUT_FOLDER, sub_folder) if sub_folder else settings.INPUT_FOLDER
        self.write_file(*args, **kwargs, project_sub_folder=sub_folder)

    def write_file_to_output(self, *args, **kwargs):
        """
        Write YAML file to OUTPUT folder.
        Same as write_file, except we add OUTPUT folder as sub_folder.
        """
        sub_folder = kwargs.pop('project_sub_folder', None)
        sub_folder = os.path.join(settings.OUTPUT_FOLDER, sub_folder) if sub_folder else settings.OUTPUT_FOLDER
        return self.write_file(*args, **kwargs, project_sub_folder=sub_folder)


class ProfileMixin(YAMLReadWriteMixin):
    """
    Profile Mixin inherits ability to read and write to profiles also
    """

    @staticmethod
    def get_profile_resource_name(profile_name, profile_config):
        return profile_config.get(RESOURCE_FILE_NAME, profile_name + ".yaml")
