import os


class Settings:

    # General Settings
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    PROJECT_FOLDER_NAME = "project"     # Name of top-level namespace where all projects are
    APP_TEMPLATE_DIRECTORY = "app_template"

    INPUT_FOLDER = "conf"
    OUTPUT_FOLDER = "build"

    SWAGGER_FILE = "swagger.yaml"
    LOCUST_FILE = "locust.py"
    ARTILLERY_FILE = "processor.js"
    ARTILLERY_YAML = "artillery.yaml"

    LOCUST_HOOK_FILE = "hooks.py"
    K6_HOOK_FILE = "hooks.js"
    MAPPING_FILE = "resource_mapping.yaml"
    RES_MAPPING_HOOKS_FILE = "resource_hooks.py"
    PROFILES_FILE = "profiles.yaml"
    RESOURCES_FOLDER = "resources"
    DIST_FOLDER = "dist"

    # Generated Output files for K6
    # Do not change these names, as they are imported as it is in JS
    K6_PROFILES = "profiles.js"
    K6_RESOURCES = "resources.js"
