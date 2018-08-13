PATHS = "paths"

OPERATION = "operationID"

# Parameter Constants
PARAMETERS = "parameters"
PARAMETER_NAME = "name"
IN_ = "in"
PATH_PARAM = "path"
RESOURCE = "resource"
BODY_PARAM = "body"
QUERY_PARAM = "query"

# Defining an Object/Schema
SCHEMA = "schema"
REF = "$ref"
PROPERTIES = "properties"

# Open API Supported Methods
GET = "get"
POST = "post"
DELETE = "delete"
PATCH = "patch"
PUT = "put"
VALID_METHODS = [GET, POST, DELETE, PATCH, PUT]

# Resource Constants
FETCH = "fetch"

RESOURCE_MAPPING = {
    GET: FETCH,
    PUT: FETCH
}

# Valid Swagger/OpenAPI extensions
JSON = "json"
YAML = "yaml"

# Data Type Maps
TYPE = "type"
FORMAT = "format"
OBJECT = "object"
INTEGER = "integer"
NUMBER = "number"
STRING = "string"
BOOLEAN = "boolean"
QUERY_TYPES = [INTEGER, NUMBER, STRING, BOOLEAN]    # Valid types for query Parameters

# Integer Options
MINIMUM = "minimum"
MAXIMUM = "maximum"
MIN_EXCLUDE = "exclusiveMinimum"
MAX_EXCLUDE = "exclusiveMaximum"
MULTIPLE_OF = "multipleOf"

# String Options
MIN_LENGTH = "minLength"
MAX_LENGTH = "maxLength"
PATTERN = "pattern"
DATE = "date"
DATE_TIME = "date-time"
PASSWORD = "password"
BYTE = "byte"
BINARY = "binary"
EMAIL = "email"
UUID = "uuid"
