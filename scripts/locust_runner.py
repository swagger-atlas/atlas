import os
import subprocess

from settings.conf import settings

file_path = os.path.join(settings.BASE_DIR, settings.PROJECT_FOLDER_NAME, settings.PROJECT_NAME, settings.OUTPUT_FOLDER,
                         settings.LOCUST_FILE)

COMMAND = "locust -f {file_path} --host={host}".format(file_path=file_path, host=settings.HOST_URL)

if __name__ == "__main__":
    command = COMMAND.split()
    subprocess.call(command)
