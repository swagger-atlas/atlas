import os


class Settings:

    # General Settings
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    PROJECT_FOLDER_NAME = "project"     # Name of top-level namespace where all projects are
    PROJECT_NAME = ""   # Overwrite this in your local file

    # Since these properties could be over-written in local file, we do not access them directly
    PROJECT_PATH = property(lambda self: os.path.join(self.BASE_DIR, self.PROJECT_FOLDER_NAME, self.PROJECT_NAME))
    PROJECT_MODULE = property(lambda self: "{}.{}".format(self.PROJECT_FOLDER_NAME, self.PROJECT_NAME))

    LOCUST_HOOK_FILE = "hooks.py"
    MAPPING_FILE = "res_mapping.yaml"
    RES_MAPPING_HOOKS_FILE = "map_hooks.py"
    RESOURCE_POOL_FILE = "resources.yaml"
    PROFILES_FILE = "profiles.yaml"
