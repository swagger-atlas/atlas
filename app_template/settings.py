class Settings:
    DATABASE = {
        "engine": "",  # Allowed values are "postgres", "mysql", "sqlite"
        "name": "",
        "user": "",
        "password": "",
        "host": "",
        "port": ""
    }

    # These APIs would not be hit during load test
    # Strings are matched via Regex Mechanism
    EXCLUDE_URLS = ["/logout", "/login"]

    SERVER_URL = {
        "protocol": "http",
        "host": "",           # if left empty, would be picked from swagger. If not there, would be localhost

        # In swagger, we search for info/url and basePath  for this setting
        "api_url": "",       # if left empty, would be picked from swagger. If not there, would be blank string.
    }

    # Page Query Parameters
    # These parameters are esp. handled, since they must be positive
    PAGE_SIZE_PARAM = 'page_size'
    PAGE_PARAM = 'page'
    POSITIVE_INTEGER_PARAMS = {PAGE_PARAM, PAGE_SIZE_PARAM}

    # This instructs Swagger whether to hit only required parameters or try optional combinations also
    HIT_ALL_QUERY_PARAMS = False

    # Only hit APIs which match Tags
    ONLY_TAG_API = False
