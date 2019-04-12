LOGOUT_URL = "POST /logout/"
LOGIN_URL = "POST /login/"


class Configuration:
    """
    Swagger Configuration
    """

    # These APIs would not be hit during load test
    EXCLUDE_URLS = [LOGOUT_URL, LOGIN_URL]

    SERVER_URL = {
        "protocol": "",  # If left empty, would be picked from swagger. If not in swagger, would be "http"
        "host": "",  # if left empty, would be picked from swagger. If not there, would be localhost

        # In swagger, we search for info/url and basePath  for this setting
        "api_url": "",  # if left empty, would be picked from swagger. If not there, would be blank string.
    }

    # Custom Ordering Dependency
    # This is an array of 2-pair tuples, with second operation being dependent on first operation
    # These are operation OP_KEYs --> Eg: [ ("POST /pet/", "GET /pet/{id}"), ("POST /pet/", "PUT /pet/{id}") ]
    SWAGGER_OPERATION_DEPENDENCIES = []

    # ### Resource Auto-detection settings
    # These suffixes if present determine whether the URL parameter is resource or not
    SWAGGER_URL_PARAM_RESOURCE_SUFFIXES = {"_id", "Id", "_slug", "Slug", "pk"}

    # These are direct names for Path parameters
    SWAGGER_PATH_PARAM_RESOURCE_IDENTIFIERS = {"id", "slug", "pk"}

    # These are field names which if present in references are marked as resource with Reference name
    SWAGGER_REFERENCE_FIELD_RESOURCE_IDENTIFIERS = {"id", "slug", "pk"}

    # #### End Resource Auto-detection constant settings

    # Custom Scenarios for Load Test.
    # See: https://github.com/swagger-atlas/atlas/blob/master/docs/profiles.md for more details
    LOAD_TEST_SCENARIOS = {}

    # #### Load Test Settings

    SPAWN_RATE = 1    # Rate at which VUs will spawn
    DURATION = 1      # Duration for which VUs will spawn and run

    # #### Load Test Settings
