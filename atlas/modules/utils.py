import os
import re

import inflection

from atlas.modules import exceptions, constants
from atlas.conf import settings

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
            raise exceptions.ImproperSwaggerException(f"Cannot find reference {ref_element} in {spec}")

    return spec


def convert_to_snake_case(name):
    intermediate_string = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', intermediate_string).lower()


def get_project_path():
    return os.getcwd()


def extract_resource_name_from_param(param_name, url_path, param_type=constants.PATH_PARAM):
    """
    Extract Resource Name from parameter name
    Names could be either snake case (foo_id) or camelCase (fooId)
    In case of URL Params, further they could be foo/id
    Return None if no such resource could be found
    """

    resource_name = None

    for suffix in settings.SWAGGER_URL_PARAM_RESOURCE_SUFFIXES:
        if param_name.endswith(suffix):
            resource_name = param_name[:-len(suffix)]
            break

    # We need to convert Param Name only after subjecting it to CamelCase Checks
    param_name = "".join([x.lower() for x in re.sub("-", "_", param_name).split("_")])

    # Resource Name not found by simple means.
    # Now, assume that resource could be available after the resource
    # For example: pets/{id} -- here most likely id refers to pet
    if (
            not resource_name and param_name in settings.SWAGGER_PATH_PARAM_RESOURCE_IDENTIFIERS
            and param_type == constants.PATH_PARAM
    ):
        url_array = url_path.split("/")
        resource_index = url_array.index(f'{{{param_name}}}') - 1
        if resource_index >= 0:
            # Singularize the resource
            resource_name = inflection.singularize(url_array[resource_index])

    return resource_name
