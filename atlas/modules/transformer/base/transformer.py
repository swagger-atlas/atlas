from io import open
import os

from atlas.modules import utils, constants
from atlas.conf import settings


class FileConfig:

    OUT_FILE = None

    def __init__(self, task_set, specs=None):
        self.task_set = task_set
        self.specs = specs or {}

    def get_imports(self):
        raise NotImplementedError

    def get_global_vars(self):
        return ""

    def convert(self):
        file_components = [
            self.get_imports(),
            self.get_global_vars(),
            self.task_set.convert(width=1)
        ]
        return "\n\n\n".join([component for component in file_components if component])

    def write_to_file(self, file_name=None):
        file_name = file_name or self.OUT_FILE
        _file = os.path.join(utils.get_project_path(), settings.OUTPUT_FOLDER, file_name)

        with open(_file, 'w') as write_file:
            write_file.write(self.convert() + "\n")  # Append EOF New line

    def get_swagger_url(self):

        protocol = settings.SERVER_URL.get('protocol')
        if not protocol:
            schemes = self.specs.get(constants.SCHEMES, [])
            protocol = schemes[0] if schemes else "http"

        host = settings.SERVER_URL.get('host')
        if not host:
            host = self.specs.get(constants.HOST, "localhost")

        api_url = settings.SERVER_URL.get('api_url')
        if not api_url:
            api_info = self.specs.get(constants.INFO, {})
            api_url = api_info.get(constants.API_URL, self.specs.get(constants.BASE_PATH, ""))

        return f"{protocol}://{host}{api_url}"
