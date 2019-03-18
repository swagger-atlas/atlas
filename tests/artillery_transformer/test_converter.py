import os
from unittest import mock

import pytest
import yaml

from atlas.modules.transformer.commands.converter import Converter
from atlas.conf import settings


class TestArtilleryConverter:

    artillery_file = os.path.join(settings.OUTPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_YAML)
    processor_file = os.path.join(settings.OUTPUT_FOLDER, settings.ARTILLERY_FOLDER, settings.ARTILLERY_FILE)

    @pytest.fixture(scope='class', autouse=True)
    @mock.patch('atlas.modules.transformer.commands.converter.yaml_to_js.Converter')
    def test_instance(self, patched_arg):
        convert = Converter()
        convert.handle(type='artillery')

        patched_arg.assert_called()

    def test_artillery_config(self):

        with open(self.artillery_file) as yaml_file:
            contents = yaml.safe_load(yaml_file)

            assert contents.get("config") and isinstance(contents["config"], dict)
            assert contents["config"] == {
                "phases": [{"arrivalRate": 1, "duration": 1}], "processor": "./processor.js",
                "target": "http://localhost:8080/v2"
            }

    def test_artillery_scenarios(self):

        with open(self.artillery_file) as yaml_file:
            contents = yaml.safe_load(yaml_file)

            assert contents.get("scenarios") and isinstance(contents["scenarios"], list)
            flow = contents["scenarios"][0]["flow"]
            assert flow == [
                {"function": "defaultSetProfiles"},
                {"function": "setUp"},
                {"post": mock.ANY},
                {"get": mock.ANY},
                {"function": "endResponse"},
            ]
            assert contents["scenarios"][0]["name"] == "default"
