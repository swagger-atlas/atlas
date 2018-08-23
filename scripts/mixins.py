from io import open
import os

import yaml

from scripts import utils


RESOURCE_FILE_NAME = "resource_file"


class ProfileMixin:

    @staticmethod
    def get_profile_resource_name(profile_name, profile_config):
        return profile_config.get(RESOURCE_FILE_NAME, profile_name + ".yaml")


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

    def write_file(self, file_name, write_data, project_sub_folder=None):
        _file = os.path.join(self.get_project_folder(project_sub_folder), file_name)

        with open(_file, 'a+') as file_stream:
            yaml.dump(write_data, file_stream, default_flow_style=False)
