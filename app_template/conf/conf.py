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
