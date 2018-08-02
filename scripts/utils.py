class StringDict(dict):
    """
    Make sure that strings could be formatted in stages

    Usage:
        (with format)
        partial_s = "{name} {country}".format(**StringDict(name="K&R"))
        --> "K&R {country}
        partial_s.format(**StringDict(country="USA"))
        --> "K&R USA"

        (with format_map)
        partial_s = "{name} {country}".format_map(StringDict(name="K&R"))
        --> "K&R {country}
        partial_s.format_map(StringDict(country="USA"))
        --> "K&R USA"

    Limitations:
        This only works for basic cases
        If you want to over-write say {foo:1.2f}, this class alone would not be sufficient.
        To achieve something like that, see: https://ideone.com/xykV7R
    """

    def __missing__(self, key):
        return "{" + key + "}"
