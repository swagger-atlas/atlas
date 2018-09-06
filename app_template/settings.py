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
    LOGOUT_API_URL = "/logout/"

    HOST_URL = ""

    # Page Query Parameters
    # These parameters are esp. handled, since they must be positive
    page_size_param = 'page_size'
    page_param = 'page'
    POSITIVE_INTEGER_PARAMS = [page_param, page_size_param]

    # This instructs Swagger whether to hit only required parameters or try optional combinations also
    HIT_ALL_QUERY_PARAMS = False
