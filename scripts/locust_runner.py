import subprocess

from settings.base import Settings

COMMAND = "locust -f {locust_path} --host={host}".format(
    locust_path=Settings.LOCUST_FILE, host=Settings.HOST_URL
)

if __name__ == "__main__":
    command = COMMAND.split()
    subprocess.call(command)
