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
_ = require('lodash');
settings = require('./settings');

const singleton = Symbol();
const singletonEnforcer = Symbol();

exports.Resource = class Resource {{
    // Resource class is singleton
    // You have to use resource.instance to get resource, and not new Resource()

    constructor(enforcer) {{
        if(enforcer !== singletonEnforcer) {{
            throw "Cannot construct Singleton";
        }}

        this.resources = {{}};

        {initial_resources}
    }}

    static get instance() {{
        if(!this[singleton]) {{
            this[singleton] = new Resource(singletonEnforcer);
        }}
        return this[singleton];
    }}

    static getKey(profile, resourceKey) {{
        return profile + ":" + resourceKey;
    }}

    getResource(profile, resourceKey, options) {{

        let values = [...this.resources[Resource.getKey(profile, resourceKey)]];

        if (options.delete || options.items === 1) {{
            let value = _.sample(values);

            if (!_.isNil(value) && options.delete) {{
                this.deleteResource(profile, resourceKey, value);
            }}

            values = _.isNil(value)  || value === "" ? [] : [value];
        }}

        return new Set(_.isEmpty(values) ? []: values);
    }}

    updateResource(profile, resourceKey, resourceValues) {{
        if (!_.isEmpty(resourceValues)) {{
            const key = Resource.getKey(profile, resourceKey);

            if (this.resources[key]) {{
                this.resources[key] = new Set([...resourceValues, ...this.resources[key]]);
            }} else {{
                this.resources[key] = resourceValues;
            }}
        }}
    }}

    deleteResource(profile, resourceKey, resourceValue) {{
        this.resources[Resource.getKey(profile, resourceKey)].delete(resourceValue);
    }}
}};
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
        out_data = "exports.profiles = {};\n".format(json.dumps(data, indent=4))

        out_file = os.path.join(self.path, settings.OUTPUT_FOLDER, settings.ARTILLERY_LIB_FOLDER, settings.K6_PROFILES)

        with open(out_file, 'w') as js_file:
            js_file.write(out_data)

    def convert_resources(self):
        _dir = os.path.join(self.path, settings.OUTPUT_FOLDER, settings.RESOURCES_FOLDER)

        profile_data = []

        for profile in self.profiles:
            _file = os.path.join(_dir, profile+".yaml")
            with open(_file) as yaml_file:
                data = yaml.safe_load(yaml_file)

            indent_width = 2
            profile_data.append(self.update_statements(profile, data, indent_width))

        profile_str = "\n".join(profile_data)
        out_data = TEMPLATE.format(initial_resources=profile_str)

        out_file = os.path.join(self.path, settings.OUTPUT_FOLDER, settings.ARTILLERY_LIB_FOLDER, settings.K6_RESOURCES)

        with open(out_file, 'w') as js_file:
            js_file.write(out_data)

    @staticmethod
    def update_statements(profile, data, indent_width):
        """
        Convert the resources into Update Statements
        Assumption being that Resources are a single level dict, with each value being set
        """
        indent = ' ' * 4 * indent_width
        out_data = [
            f"this.updateResource('{profile}', '{key}', new Set({list(value)}));" for key, value in data.items()
        ]
        return f"\n{indent}".join(out_data)

    def convert(self):
        self.convert_profiles()
        self.convert_resources()
