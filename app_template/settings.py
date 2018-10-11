class Settings:
    DATABASE = {
        "engine": "",  # Allowed values are "postgres", "mysql", "sqlite"
        "name": "",
        "user": "",
        "password": "",
        "host": "",
        "port": ""
    }

    # This API would not be hit during load test
    EXCLUDE_URLS = ["/logout/"]

    HOST_URL = ""

    # Page Query Parameters
    # These parameters are esp. handled, since they must be positive
    PAGE_SIZE_PARAM = 'page_size'
    PAGE_PARAM = 'page'
    POSITIVE_INTEGER_PARAMS = {PAGE_PARAM, PAGE_SIZE_PARAM}

    # This instructs Swagger whether to hit only required parameters or try optional combinations also
    HIT_ALL_QUERY_PARAMS = False

    # Only hit APIs which match Tags
    ONLY_TAG_API = False

    # REDIS URL
    REDIS_SERVER_URL = "http://localhost:7379"
