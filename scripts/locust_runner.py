import os
import subprocess

from settings.conf import settings

file_path = os.path.join(settings.BASE_DIR, settings.PROJECT_FOLDER_NAME, settings.PROJECT_NAME, settings.OUTPUT_FOLDER,
                         settings.LOCUST_FILE)

options = [
    "-f {file_path}".format(file_path=file_path),
    "--host={host}".format(host=settings.HOST_URL),
    "--clients 10",
    "--hatch-rate 1",
    "--no-web",
    "--num-request 100",
    "--only-summary"
]

COMMAND = "locust {options}".format(options=" ".join(options))


if __name__ == "__main__":
    command = COMMAND.split()
    subprocess.call(command)
