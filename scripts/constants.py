PATHS = "paths"

OPERATION = "operationID"

# Parameter Constants
PARAMETERS = "parameters"
PARAMETER_NAME = "name"
IN_ = "in"
PATH_PARAM = "path"
RESOURCE = "resource"

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
INTEGER = "integer"
NUMBER = "number"
STRING = "string"

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
