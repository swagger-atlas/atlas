import os


class Settings:

    # General Settings
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    # Locust Settings
    LOCUST_FILE = "locust_config.py"
