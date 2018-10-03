# Note: This file is converted to JS equivalent
# So keep this simple and only add key value types which have JS equivalent

PATHS = "paths"

OPERATION = "operationId"
TAGS = "tags"
RESPONSES = "responses"
VALID_RESPONSES = {'200', '201', '204'}

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
REQUIRED = "required"
URL_PARAMS = {PATH_PARAM, QUERY_PARAM}

# Defining an Object/Schema
SCHEMA = "schema"
REF = "$ref"
PROPERTIES = "properties"
READ_ONLY = "readOnly"
TITLE = "title"
DESCRIPTION = "description"
ALL_OF = "allOf"
ADDITIONAL_PROPERTIES = "additionalProperties"
MIN_PROPERTIES = "minProperties"

# Open API Supported Methods
GET = "get"
POST = "post"
DELETE = "delete"
PATCH = "patch"
PUT = "put"
VALID_METHODS = {GET, POST, DELETE, PATCH, PUT}

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
QUERY_TYPES = {INTEGER, NUMBER, STRING, BOOLEAN, ARRAY}    # Valid types for query Parameters

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
URI = "uri"
SLUG = "slug"

# Array Options
MIN_ITEMS = "minItems"
MAX_ITEMS = "maxItems"
ITEMS = "items"
UNIQUE_ITEMS = "uniqueItems"

# References
DEFINITIONS = "definitions"

# Extra Keys for Data Providers
EXTRA_KEYS = {PARAMETER_NAME, IN_, READ_ONLY, REQUIRED, TITLE}
