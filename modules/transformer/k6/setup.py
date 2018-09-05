from io import open
import os

import requests
import six

from modules import constants
from settings.conf import settings


LIBS = {
    # Please do not change the names of keys as we have imported the packages in multiple locations with these names
    "lodash": "https://raw.githubusercontent.com/lodash/lodash/4.17.10-npm/lodash.min.js",
    "faker": "https://cdnjs.cloudflare.com/ajax/libs/Faker/3.1.0/faker.min.js",
    "yaml": "https://cdnjs.cloudflare.com/ajax/libs/yamljs/0.3.0/yaml.min.js",
}

BOOL_MAP = {
    False: "false",
    True: "true"
}


class K6Setup:

    def __init__(self):
        self.js_lib_path = os.path.join(settings.BASE_DIR, "js_libs")

    def ensure_js_lib_dir(self):
        if not os.path.exists(self.js_lib_path):
            os.makedirs(self.js_lib_path)

    def create_vendor_libraries(self):
        for key, value in LIBS.items():
            out_file = os.path.join(self.js_lib_path, "{}.js".format(key))
            resp = requests.get(value)
            with open(out_file, "w+") as out_stream:
                out_stream.write(resp.text)

    @staticmethod
    def convert_python_vars_to_js_exports(python_vars, python_object):

        out_data = []
        for item in python_vars:

            # Ignore the dunder variables, since there are high chances it is python built-in
            if item.startswith("__"):
                continue

            value = getattr(python_object, item)

            js_val = None

            if isinstance(value, six.string_types):
                js_val = "'{}'".format(value)
            elif isinstance(value, bool):       # This should be checked before integer
                js_val = BOOL_MAP[value]
            elif isinstance(value, int):
                js_val = value
            elif isinstance(value, (list, tuple)):
                js_val = list(value)
            elif isinstance(value, set):
                js_val = "new Set({})".format(list(value))
            else:
                # While this may not necessarily be an error, we do not convert it.
                # This includes any Dict structure for now
                print("No compatible data found - {} {}".format(item, value))

            if js_val is not None:
                out_data.append("export const {} = {};".format(item, js_val))

        return out_data

    def constants_file(self):
        out_file = os.path.join(self.js_lib_path, "constants.js")
        out_data = self.convert_python_vars_to_js_exports(dir(constants), constants)

        with open(out_file, "w+") as out_stream:
            out_stream.write("\n".join(out_data) + "\n")

    def settings_file(self):
        out_file = os.path.join(self.js_lib_path, "settings.js")
        out_data = self.convert_python_vars_to_js_exports(dir(settings), settings)

        with open(out_file, "w+") as out_stream:
            out_stream.write("\n".join(out_data) + "\n")

    def setup(self):
        self.ensure_js_lib_dir()
        self.create_vendor_libraries()
        self.constants_file()
        self.settings_file()


if __name__ == "__main__":
    setup = K6Setup()
    setup.setup()
