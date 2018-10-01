from io import open
import json
import os
import yaml

from atlas.conf import settings
from atlas.modules import utils


BOOL_MAP = {
    False: "false",
    True: "true"
}


TEMPLATE = """
const singleton = Symbol();
const singletonEnforcer = Symbol();

export class Resource {{
    // Resource class is singleton
    // You have to use resource.instance to get resource, and not new Resource()

    constructor(enforcer) {{
        if(enforcer !== singletonEnforcer) {{
            throw "Cannot construct Singleton";
        }}

        this.resources = {{
            {resource}
        }};
    }}

    static get instance() {{
        if(!this[singleton]) {{
            this[singleton] = new Resource(singletonEnforcer);
        }}
        return this[singleton];
    }}

    updateResource(profile, resourceKey, resourceValues) {{
        this.resources[profile][resourceKey] = resourceValues;
    }}
}}
"""


class Converter:
    """
    Converts YAML file to JS file.
    This helps in reducing file read at runtime
    This also reduces the need for libraries needed to parse YAML in thread load
    """

    def __init__(self):
        self.profiles = []
        self.path = utils.get_project_path()

    def convert_profiles(self):
        _file = os.path.join(self.path, settings.INPUT_FOLDER, settings.PROFILES_FILE)
        with open(_file) as yaml_file:
            data = yaml.safe_load(yaml_file)

        self.profiles = data.keys()
        out_data = "export const profiles = {};\n".format(json.dumps(data, indent=4))

        out_file = os.path.join(self.path, settings.OUTPUT_FOLDER, settings.K6_PROFILES)

        with open(out_file, 'w') as js_file:
            js_file.write(out_data)

    def convert_resources(self):
        _dir = os.path.join(self.path, settings.OUTPUT_FOLDER, settings.RESOURCES_FOLDER)

        profile_data = []

        for profile in self.profiles:
            _file = os.path.join(_dir, profile+".yaml")
            with open(_file) as yaml_file:
                data = yaml.safe_load(yaml_file)

            indent_width = 3

            indent = " "*4*indent_width
            profile_data.append("{key}: {{\n{value}\n{indent}}}".format(
                key=profile, value=self.serialize_resources(data, indent_width+1), indent=indent
            ))

        profile_str = ",\n".join(profile_data)
        # out_data = "export const resources = {{\n{}\n}};\n".format(profile_str)
        out_data = TEMPLATE.format(resource=profile_str)

        out_file = os.path.join(self.path, settings.OUTPUT_FOLDER, settings.K6_RESOURCES)

        with open(out_file, 'w') as js_file:
            js_file.write(out_data)

    @staticmethod
    def serialize_resources(data, indent_width):
        """
        Serialize the Resource to JS conventions
        Assumption being that Resources are a single level dict, with each value being set
        We cannot simply use JSON, since it is not YAML dict
        """

        indent = ' '*4*indent_width
        out_data = ["{}{}: new Set({})".format(indent, key, list(value)) for key, value in data.items()]
        return ",\n".join(out_data)

    def convert(self):
        self.convert_profiles()
        self.convert_resources()
