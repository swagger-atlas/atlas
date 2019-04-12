class Settings:

    # APP DB Settings.
    # Required if you add any DB Mapping in conf/resource_mapping.yaml
    # Reference: https://github.com/swagger-atlas/atlas/blob/master/docs/resources.md
    DATABASE = {
        "engine": "",  # Allowed values are "postgres", "mysql", "sqlite"
        "name": "",
        "user": "",
        "password": "",
        "host": "",
        "port": ""
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

    # INFLUX DB Setting. Required.
    # Default settings are ones used by Docker.
    # If you change them, you would need to update docker-compose to work
    # Database name is used by Grafana as data source.
    # So, any update in name would require you to manually update grafana dashboard
    INFLUX = {
        "database": "atlas",
        "host": "localhost",
        "port": "9086",
        "username": "admin",
        "password": "admin"
    }
