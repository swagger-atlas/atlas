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
    ROUTES_FILE = "routes.py"
    RES_MAPPING_HOOKS_FILE = "hooks.py"
    PROFILES_FILE = "profiles.yaml"
    RESOURCES_FOLDER = "resources"
    DIST_FOLDER = "dist"

    LOCUST_FILE = "locust.py"
    LOCUST_HOOK_FILE = "hooks.py"

    # Generated Output files for Artillery
    # Do not change these names, as they are imported as it is in JS
    ARTILLERY_LIB_FOLDER = "libs"
    ARTILLERY_FOLDER = "artillery"
    ARTILLERY_PROFILES = "profiles.js"
    ARTILLERY_RESOURCES = "resources.js"
    ARTILLERY_FILE = "processor.js"
    ARTILLERY_YAML = "artillery.yaml"
    ARTILLERY_HOOK_FILE = "hooks.js"

    # These APIs would not be hit during load test
    EXCLUDE_URLS = []

    SERVER_URL = {
        "protocol": "",  # If left empty, would be picked from swagger. If not in swagger, would be "http"
        "host": "",  # if left empty, would be picked from swagger. If not there, would be localhost

        # In swagger, we search for info/url and basePath  for this setting
        "api_url": "",  # if left empty, would be picked from swagger. If not there, would be blank string.
    }

    # Custom Ordering Dependency
    # This is an array of 2-pair tuples, with second operation being dependent on first operation
    # These are operation IDs --> Eg: [ (petCreate, petList), (petCreate, petRetrieve) ]
    SWAGGER_OPERATION_DEPENDENCIES = []

    # ### Resource Auto-detection settings
    # These suffixes if present determine whether the URL parameter is resource or not
    SWAGGER_URL_PARAM_RESOURCE_SUFFIXES = {"_id", "Id", "_slug", "Slug", "pk"}

    # These are direct names for Path parameters
    SWAGGER_PATH_PARAM_RESOURCE_IDENTIFIERS = {"id", "slug", "pk"}

    # These are field names which if present in references are marked as resource with Reference name
    SWAGGER_REFERENCE_FIELD_RESOURCE_IDENTIFIERS = {"id", "slug", "pk"}

    # #### End Resource Auto-detection constant settings

    LOAD_TEST_SCENARIOS = {}
