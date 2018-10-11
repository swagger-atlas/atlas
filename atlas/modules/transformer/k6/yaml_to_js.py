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
import http from 'k6/http'
import _ from 'js_libs/lodash.js'
import * as settings from 'js_libs/settings.js'

const singleton = Symbol();
const singletonEnforcer = Symbol();

export class Resource {{
    // Resource class is singleton
    // You have to use resource.instance to get resource, and not new Resource()

    constructor(enforcer) {{
        if(enforcer !== singletonEnforcer) {{
            throw "Cannot construct Singleton";
        }}

        this.db_url = settings.REDIS_SERVER_URL;

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

        let command = "smembers";
        let isSingle = false;

        if (options.delete) {{
            command = "spop";
            isSingle = true;
        }} else if (options.items === 1) {{
            command = "srandmember";
            isSingle = true;
        }}

        let resp = http.post(this.db_url, command + "/" + Resource.getKey(profile, resourceKey));
        let values = resp.json()[command];

        if (isSingle) {{
            values = _.isNil(values)  || values === "" ? [] : [values];
        }}

        return new Set(_.isEmpty(values) ? []: values);
    }}

    updateResource(profile, resourceKey, resourceValues) {{
        if (!_.isEmpty(resourceValues)) {{
            http.post(this.db_url, "sadd/" + Resource.getKey(profile, resourceKey) + "/" + _.join([...resourceValues], '/'));
        }}
    }}

    deleteResource(profile, resourceKey, resourceValue) {{
        http.post(this.db_url, "srem/" + Resource.getKey(profile, resourceKey) + "/" + resourceValue);
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

            indent_width = 2
            profile_data.append(self.redis_statements(profile, data, indent_width))

        profile_str = "\n".join(profile_data)
        out_data = TEMPLATE.format(initial_resources=profile_str)

        out_file = os.path.join(self.path, settings.OUTPUT_FOLDER, settings.K6_RESOURCES)

        with open(out_file, 'w') as js_file:
            js_file.write(out_data)

    @staticmethod
    def redis_statements(profile, data, indent_width):
        """
        Convert the resources into Redis Statements
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
