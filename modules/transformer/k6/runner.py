import os
import subprocess

from settings.conf import settings

file_path = os.path.join(settings.BASE_DIR, settings.PROJECT_FOLDER_NAME, settings.PROJECT_NAME, settings.OUTPUT_FOLDER,
                         settings.K6_FILE)

options = [
    "{file_path}".format(file_path=file_path),
    "--vus 10",
    "--duration 30s"
]


COMMAND = "k6 run {options}".format(options=" ".join(options))


if __name__ == "__main__":
    command = COMMAND.split()
    subprocess.call(command)
