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
    def get_project_folder(sub_folder=None):

        project_path = utils.get_project_path()

        if sub_folder:
            project_path = os.path.join(project_path, sub_folder)

        return project_path

    def read_file(self, file_name, default_value=None, project_sub_folder=None):

        _file = os.path.join(self.get_project_folder(project_sub_folder), file_name)

        try:
            with open(_file) as file_stream:
                ret_stream = yaml.safe_load(file_stream)
        except FileNotFoundError:
            ret_stream = default_value

        return ret_stream or default_value

    def read_file_from_input(self, *args, **kwargs):
        sub_folder = kwargs.pop('project_sub_folder', None)
        sub_folder = os.path.join(settings.INPUT_FOLDER, sub_folder) if sub_folder else settings.INPUT_FOLDER
        return self.read_file(*args, **kwargs, project_sub_folder=sub_folder)

    def read_file_from_output(self, *args, **kwargs):
        sub_folder = kwargs.pop('project_sub_folder', None)
        sub_folder = os.path.join(settings.OUTPUT_FOLDER, sub_folder) if sub_folder else settings.OUTPUT_FOLDER
        return self.read_file(*args, **kwargs, project_sub_folder=sub_folder)

    def write_file(self, file_name, write_data, project_sub_folder=None, append_mode=True, force_write=False):
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
        sub_folder = kwargs.pop('project_sub_folder', None)
        sub_folder = os.path.join(settings.INPUT_FOLDER, sub_folder) if sub_folder else settings.INPUT_FOLDER
        self.write_file(*args, **kwargs, project_sub_folder=sub_folder)

    def write_file_to_output(self, *args, **kwargs):
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
