import os
import re

import inflection

from atlas.modules import exceptions, constants
from atlas.conf import settings

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def get_ref_path_array(ref_definition: str) -> list:
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


def operation_id_name(url, method) -> str:
    """
    Generate the name for Operation ID

    Logic:
        user/       - (user_create, user_list)
        user/{id}   - (user_read, user_update, user_delete)
        user/{id}/action - (user_action with above logic)
    """

    url_fragments = [fragment for fragment in url.split("/") if fragment]

    counter = 1
    op_name_array = []

    for url_element in url_fragments:
        if url_element.startswith("{"):
            op_name_array.append(f"PARAM_{counter}")
            counter += 1
        else:
            op_name_array.append(url_element)

    if method == constants.DELETE:
        op_name_array.append("delete")
    elif method == constants.GET:
        op_name_array.append("read" if url_fragments[-1].startswith("{") else "list")
    else:
        if method == constants.POST:
            _name = "create"
        elif method == constants.PATCH:
            _name = "partial_update"
        else:
            _name = "update"
        op_name_array.append(_name)

    return "_".join(op_name_array)
