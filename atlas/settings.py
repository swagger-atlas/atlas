import os


class Settings:

    # General Settings
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    PROJECT_FOLDER_NAME = "project"     # Name of top-level namespace where all projects are
    APP_TEMPLATE_DIRECTORY = "app_template"
    EXAMPLE_DIRECTORY = "examples"

    INPUT_FOLDER = "conf"
    OUTPUT_FOLDER = "build"

    SWAGGER_FILE = "swagger.yaml"
    MAPPING_FILE = "resource_mapping.yaml"
    RES_MAPPING_HOOKS_FILE = "resource_hooks.py"
    PROFILES_FILE = "profiles.yaml"
    RESOURCES_FOLDER = "resources"
    DIST_FOLDER = "dist"

    LOCUST_FILE = "locust.py"
    LOCUST_HOOK_FILE = "hooks.py"

    # Generated Output files for Artillery
    # Do not change these names, as they are imported as it is in JS
    ARTILLERY_LIB_FOLDER = "libs"
    ARTILLERY_PROFILES = "profiles.js"
    ARTILLERY_RESOURCES = "resources.js"
    ARTILLERY_FILE = "processor.js"
    ARTILLERY_YAML = "artillery.yaml"
    ARTILLERY_HOOK_FILE = "hooks.js"

    # ### Resource Auto-detection settings
    # These suffixes if present determine whether the URL parameter is resource or not
    URL_PARAM_RESOURCE_SUFFIX = {"_id", "Id", "_slug", "Slug", "pk"}

    # These are direct names for Path parameters
    PATH_PARAM_RESOURCES = {"id", "slug", "pk"}

    # These are field names which if present in references are marked as resource with Reference name
    REFERENCE_FIELD_RESOURCES = {"id", "slug", "pk"}

    # #### End Resource Auto-detection constant settings
