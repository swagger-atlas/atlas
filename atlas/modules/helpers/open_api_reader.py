from io import open
import json
import os

import six
import yaml

from atlas.modules import (
    constants,
    exceptions,
    utils,
)
from atlas.conf import settings


class SpecsFile:

    CONVERTER = {
        constants.JSON: json.load,
        constants.YAML: yaml.safe_load
    }

    def __init__(self, spec_file=None, converter=None):
        """
        :param spec_file: Specification File Name
        :param converter: Which converter to use (JSON or YAML). Leave Null to let converter identify on its own
        """

        self.spec_file = spec_file or settings.SWAGGER_FILE
        self.converter = converter

        if isinstance(self.converter, six.string_types):
            self.converter = self.converter.lower()

        if self.converter not in {constants.JSON, constants.YAML}:
            self.identify_converter()

    def identify_converter(self):

        if self.spec_file.endswith(constants.JSON):
            self.converter = constants.JSON
        elif self.spec_file.endswith(constants.YAML):
            self.converter = constants.YAML
        else:
            raise exceptions.ImproperSwaggerException("Incorrect extension for {}".format(self.spec_file))

    def file_load(self):
        _file = os.path.join(utils.get_project_path(), settings.OUTPUT_FOLDER, self.spec_file)

        with open(_file) as open_api_file:
            ret_stream = self.CONVERTER[self.converter](open_api_file)

        return ret_stream

    def inp_file_load(self):
        _file = os.path.join(utils.get_project_path(), settings.INPUT_FOLDER, self.spec_file)

        with open(_file) as open_api_file:
            ret_stream = self.CONVERTER[self.converter](open_api_file)

        return ret_stream
