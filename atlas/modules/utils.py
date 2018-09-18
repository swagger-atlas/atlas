import os
import re

from atlas.modules import exceptions

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


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


def get_ref_path_array(ref_definition: str):
    """
    Find the reference path through its definition
    """

    # Find out which reference it is:
    if ref_definition.startswith("#/"):
        ref = ref_definition[2:].split("/")  # Ignore #/ and split the rest of string by /

    else:
        raise exceptions.ImproperSwaggerException("We only support Local references")

    return ref


def get_ref_name(ref_definition: str):
    """
    Find the reference name
    """
    return get_ref_path_array(ref_definition)[-1]


def resolve_reference(spec, ref_definition):
    """
    Resolve Reference for Swagger and return the referred part
    :param spec: Swagger specification
    :param ref_definition: Path to reference
    :return: Reference object
    """

    for ref_element in get_ref_path_array(ref_definition):
        spec = spec.get(ref_element)

        if not spec:
            raise exceptions.ImproperSwaggerException("Cannot find reference {ref} in {spec}".format(
                ref=ref_element, spec=spec
            ))

    return spec


def convert_to_snake_case(name):
    intermediate_string = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', intermediate_string).lower()


def get_project_path():
    return os.getcwd()
