from io import open
import os

import requests
import six

from modules import constants
from settings.conf import settings


LIBS = {
    "lodash": "https://raw.githubusercontent.com/lodash/lodash/4.17.10-npm/lodash.js",
    "dynamicTemplate": "https://raw.githubusercontent.com/mikemaccana/dynamic-template/master/index.js",
    "faker": "https://raw.githubusercontent.com/Marak/faker.js/master/build/build/faker.js",
    "luxon": "https://moment.github.io/luxon/global/luxon.js",
    "yaml": "https://cdnjs.cloudflare.com/ajax/libs/yamljs/0.3.0/yaml.js",
}

BOOL_MAP = {
    False: "false",
    True: "true"
}


class K6Setup:

    @property
    def js_lib_path(self):
        return os.path.join(settings.BASE_DIR, "js_libs")

    def js_libs(self):
        for key, value in LIBS.items():
            out_file = os.path.join(self.js_lib_path, "{}.js".format(key))
            resp = requests.get(value)
            with open(out_file, "w") as out_stream:
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

        with open(out_file, "w") as out_stream:
            out_stream.write("\n".join(out_data) + "\n")

    def settings_file(self):
        out_file = os.path.join(self.js_lib_path, "settings.js")
        out_data = self.convert_python_vars_to_js_exports(dir(settings), settings)

        with open(out_file, "w") as out_stream:
            out_stream.write("\n".join(out_data) + "\n")

    def setup(self):
        self.constants_file()
        self.js_libs()
        self.settings_file()


if __name__ == "__main__":
    setup = K6Setup()
    setup.setup()
