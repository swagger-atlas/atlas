class ImproperSwaggerException(Exception):
    """
    To be raised when specification does not match with OPEN API Specs
    """


class ResourcesException(Exception):
    """
    To be raised if encountered any issues in resources
    """


class ImproperInterfaceException(Exception):
    """
    To be raised if interface is used incorrectly
    """


class OrderingException(Exception):
    """
    To be raised if there is an issue while trying to order the graph
    """


class InvalidSettingsException(Exception):
    """
    TO be raised if user enters incorrect settings/configuration
    """
