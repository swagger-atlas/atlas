import os


class Settings:

    # General Settings
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    PROJECT_FOLDER_NAME = "project"     # Name of top-level namespace where all projects are
    LOCUST_HOOK_FILE = "hooks.py"
    MAPPING_FILE = "res_mapping.yaml"
    RES_MAPPING_HOOKS_FILE = "map_hooks.py"
    RESOURCE_POOL_FILE = "resources.yaml"
