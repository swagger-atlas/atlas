PATHS = "paths"

OPERATION = "operationId"

# Parameter Constants
PARAMETERS = "parameters"
PARAMETER_NAME = "name"
IN_ = "in"
PATH_PARAM = "path"
RESOURCE = "resource"
BODY_PARAM = "body"
QUERY_PARAM = "query"
FORM_PARAM = "formData"
HEADER_PARAM = "header"

# Defining an Object/Schema
SCHEMA = "schema"
REF = "$ref"
PROPERTIES = "properties"
READ_ONLY = "readOnly"

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
    GET: FETCH
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
ARRAY = "array"
ENUM = "enum"   # Strictly not a type, but is associated with both strings and numbers
QUERY_TYPES = [INTEGER, NUMBER, STRING, BOOLEAN, ARRAY]    # Valid types for query Parameters

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

# Array Options
MIN_ITEMS = "minItems"
MAX_ITEMS = "maxItems"
ITEMS = "items"
UNIQUE_ITEMS = "uniqueItems"

# References
DEFINITIONS = "definitions"
