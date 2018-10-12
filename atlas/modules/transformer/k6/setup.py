from io import open
import os

import requests
import six

from atlas.modules import constants
from atlas.conf import settings


LIBS = {
    # Please do not change the names of keys as we have imported the packages in multiple locations with these names
    "lodash": "https://raw.githubusercontent.com/lodash/lodash/4.17.10-npm/lodash.min.js",
    "faker": "https://raw.githubusercontent.com/JoshLabs/faker.js/master/build/build/faker.min.js"
}

BOOL_MAP = {
    False: "false",
    True: "true"
}


class K6Setup:

    def __init__(self):
        self.js_lib_path = os.path.join(os.getcwd(), "js_libs")

    def ensure_js_lib_dir(self):
        if not os.path.exists(self.js_lib_path):
            os.makedirs(self.js_lib_path)

    def create_vendor_libraries(self):
        for key, value in LIBS.items():
            out_file = os.path.join(self.js_lib_path, "{}.js".format(key))
            resp = requests.get(value)
            with open(out_file, "w+") as out_stream:
                out_stream.write(resp.text)

    def convert_python_value_to_js_value(self, python_value, var_name, stringify=True):
        js_val = None

        if isinstance(python_value, six.string_types):
            js_val = f"'{python_value}'" if stringify else python_value
        elif isinstance(python_value, bool):  # This should be checked before integer
            js_val = BOOL_MAP[python_value]
        elif isinstance(python_value, int):
            js_val = python_value
        elif isinstance(python_value, (list, tuple)):
            js_val = list(python_value)
        elif isinstance(python_value, set):
            js_val = "new Set({})".format(list(python_value))
        elif hasattr(python_value, "__call__"):
            js_val = None  # It is a duck-typed function, and should not be copied over
        elif isinstance(python_value, dict):
            js_val = {}
            for key, value in python_value.items():
                item_val = self.convert_python_value_to_js_value(value, key, False)
                if item_val is not None:
                    js_val[key] = item_val
        else:
            # While this may not necessarily be an error, we do not convert it.
            # This includes any Dict structure for now
            print(f"No compatible data found - {var_name} {python_value}")

        return js_val

    def get_js_exports(self, python_vars, python_object):

        out_data = []
        for item in python_vars:

            # Ignore the dunder variables, since there are high chances it is python built-in
            if item.startswith("__"):
                continue

            value = getattr(python_object, item)

            js_val = self.convert_python_value_to_js_value(value, item)

            if js_val is not None:
                out_data.append(f"export const {item} = {js_val};")

        return out_data

    def constants_file(self):
        out_file = os.path.join(self.js_lib_path, "constants.js")
        out_data = self.get_js_exports(dir(constants), constants)

        with open(out_file, "w+") as out_stream:
            out_stream.write("\n".join(out_data) + "\n")

    def settings_file(self):
        out_file = os.path.join(self.js_lib_path, "settings.js")
        out_data = self.get_js_exports(dir(settings), settings)

        with open(out_file, "w+") as out_stream:
            out_stream.write("\n".join(out_data) + "\n")

    def setup(self):
        self.ensure_js_lib_dir()
        self.create_vendor_libraries()
        self.constants_file()
        self.settings_file()
