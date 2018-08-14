import subprocess

from settings.conf import settings

COMMAND = "locust -f ../locust_config/{file} --host={host}".format(
    file=settings.LOCUST_FILE, host=settings.HOST_URL
)

if __name__ == "__main__":
    command = COMMAND.split()
    subprocess.call(command)
