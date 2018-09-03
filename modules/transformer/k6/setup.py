from io import open
import os

import requests
import six

from modules import constants
from settings.conf import settings


LIBS = {
    "lodash": "https://raw.githubusercontent.com/lodash/lodash/4.17.10-npm/lodash.js",
    "dynamicTemplate": "https://raw.githubusercontent.com/mikemaccana/dynamic-template/master/index.js",
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

    def constants_file(self):
        out_file = os.path.join(self.js_lib_path, "constants.js")
        out_data = []

        for item in dir(constants):
            if item.startswith("__"):
                continue

            value = getattr(constants, item)

            if isinstance(value, six.string_types):
                out_data.append("export const {} = '{}';".format(item, value))
            elif isinstance(value, int):
                out_data.append("export const {} = {};".format(item, value))
            elif isinstance(value, (list, tuple)):
                out_data.append("export const {} = {};".format(item, list(value)))
            elif isinstance(value, set):
                out_data.append("export const {} = new Set({});".format(item, list(value)))
            else:
                print("No compatible data found - {} {}".format(item, value))

        with open(out_file, "w") as out_stream:
            out_stream.write("\n".join(out_data) + "\n")

    def setup(self):
        self.constants_file()
        self.js_libs()


if __name__ == "__main__":
    setup = K6Setup()
    setup.setup()
