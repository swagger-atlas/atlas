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
    K6_FILE = "k6.js"

    LOCUST_HOOK_FILE = "hooks.py"
    K6_HOOK_FILE = "hooks.js"
    MAPPING_FILE = "resource_mapping.yaml"
    RES_MAPPING_HOOKS_FILE = "resource_hooks.py"
    PROFILES_FILE = "profiles.yaml"
    RESOURCES_FOLDER = "resources"
    DIST_FOLDER = "dist"

    # Page Query Parameters
    # These parameters are esp. handled, since they must be positive
    page_size_param = 'page_size'
    page_param = 'page'
    POSITIVE_INTEGER_PARAMS = [page_param, page_size_param]

    # This instructs Swagger whether to hit only required parameters or try optional combinations also
    HIT_ALL_QUERY_PARAMS = False
