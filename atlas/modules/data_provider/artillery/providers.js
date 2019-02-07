_ = require("lodash");
faker = require("faker");

constants = require('./constants');
settings = require('./settings');
Resource = require("./resources").Resource;
relatedResources = require("./relationResources").relationshipResource;

/*
        Custom Exception Definitions
 */

class InvalidDataOptionsError extends Error {}

class EmptyResourceError extends Error {}

/*
    End Exceptions Definition
 */

const LIMIT = Math.pow(10, 2);
const MILLISECONDS_IN_YEAR = 86400 * 365.25 * 1000;     // Seconds in day * avg. number of days in years * ms in sec


const FakeData = {

    getFakeMapper: function(config) {

        const itemType = _.get(config, constants.TYPE);

        if (!itemType) {
            throw new InvalidDataOptionsError(`Item type must be defined - ${JSON.stringify(config)}`);
        }

        const itemFormat = _.get(config, constants.FORMAT);

        const map = FakeData.FAKE_MAP();
        let fakeFunc = map[[itemType, itemFormat]];

        // If it did not match, try to match any format
        if (!fakeFunc)
            fakeFunc = map[[itemType, "$any"]];

        return fakeFunc;
    },

    FAKE_MAP: function (){
        // (Type, format) --> function. None should match to no format. any accepts any format at all
        let MAP = {};

        // Defined one by one instead of one go since we want to use composite keys
        MAP[[constants.INTEGER, null]] = FakeData.getInteger;
        MAP[[constants.INTEGER, "$any"]] = FakeData.getInteger;
        MAP[[constants.NUMBER, null]] = FakeData.getFloat;
        MAP[[constants.NUMBER, "$any"]] = FakeData.getFloat;
        MAP[[constants.STRING, null]] = FakeData.getString;
        MAP[[constants.STRING, constants.DATE]] = FakeData.getDate;
        MAP[[constants.STRING, constants.DATE_TIME]] = FakeData.getDateTime;
        MAP[[constants.STRING, constants.PASSWORD]] = FakeData.getPassword;
        MAP[[constants.STRING, constants.BYTE]] = FakeData.getBase64;
        MAP[[constants.STRING, constants.EMAIL]] = FakeData.getEmail;
        MAP[[constants.STRING, constants.URI]] = FakeData.getURI;
        MAP[[constants.STRING, constants.URL]] = FakeData.getURL;
        MAP[[constants.STRING, constants.SLUG]] = FakeData.getSlug;
        MAP[[constants.STRING, constants.UUID]] = FakeData.getUUID;
        MAP[[constants.STRING, constants.STRING_JSON]] = FakeData.getStringJSON;
        MAP[[constants.BOOLEAN, null]] = FakeData.getBoolean;

        return MAP;
    },

    getInteger: function(config) {
        let value = FakeData.getEnum(config);

        if (_.isNull(value)) {
            value = _.random(...FakeData.getRange(config)) * _.get(config, constants.MULTIPLE_OF, 1);
        }

        return value;
    },

    getFloat: function(config) {
        // Short-circuit return
        const num = FakeData.getEnum(config);
        if (!_.isNull(num)) {
            return num;
        }

        const minMaxArray = FakeData.getRange(config);
        let minimum = minMaxArray[0], maximum = minMaxArray[1];
        const leftSide = _.random(minimum, maximum);
        const rightSide = +Math.random().toFixed(2);        // Plus to convert it back into integer

        let finalNumber = leftSide + rightSide;

        if (finalNumber > maximum) {
            finalNumber = +maximum.toFixed(2);
        }

        if (finalNumber < minimum) {
            finalNumber = +minimum.toFixed(2);
        }

        return finalNumber
    },

    getString: function(config) {
        let value = FakeData.getEnum(config);

        if (_.isNull(value)) {

            // Make sure that we have some buffer characters if possible, and are not working at MAX
            value = faker.lorem.text().substring(0, FakeData.getOptions(config)["length"]);
        }

        return value;
    },

    getStringJSON: function(config) {
        return {};
    },

    getDate: function(config) {
        const date = FakeData.getRandomDateTime(config);
        return `${date.getUTCFullYear()}-${("0" + (date.getUTCMonth() + 1)).slice(-2)}-${("0" + date.getUTCDate()).slice(-2)}`;
    },

    getDateTime: function(config) {
        return FakeData.getRandomDateTime(config).toISOString();
    },

    getURI: function(config) {
        return faker.internet.avatar();
    },

    getURL: function(config) {
        // Not using faker.internet.url directly to control length of URL
        return faker.internet.protocol() + '://' +
            faker.name.firstName().substring(0, 5).replace(/([\\~#&*{}/:<>?|\"'])/ig, '').toLowerCase() +
            "." + faker.internet.domainSuffix();
    },

    getSlug: function(config) {
        return faker.helpers.slugify(faker.internet.userName());
    },

    getPassword: function(config) {
        let value = FakeData.getEnum(config);

        if (_.isNull(value)) {
            value = faker.internet.password(FakeData.getOptions(config)["length"]);
        }

        return value;
    },

    getBase64: function(config) {
        return Buffer.from(FakeData.getString(config)).toString('base64');
    },

    getEmail: function(config) {
        let value = FakeData.getEnum(config);

        if (_.isNull(value)) {
            value = faker.internet.email();
        }

        return value;
    },

    getUUID: function(config) {
        return faker.random.uuid();
    },

    getBoolean: function(config) {
        return faker.random.boolean();
    },

    getRandomDateTime: function(config) {
        // Date time between now to 1 year in future (approx.)
        const now = _.now();
        const start = now;
        const end = now + MILLISECONDS_IN_YEAR;
        return new Date(_.random(start, end));
    },

    getOptions: function(config) {
        /*
        Swagger supports following options:
            - MinLength
            - MaxLength
            - Pattern

        We are only supporting MaxLength, MinLength for now
        */

        let max = _.get(config, constants.MAX_LENGTH, 10);
        let min = _.get(config, constants.MIN_LENGTH, 1);

        // We want to generate a string which is shorter than maximum, but always equal to or exceeding minimum
        return {
            "length": Math.max(~~max/2, min)
        };
    },

    getEnum: function(config) {
        const enumOptions = _.get(config, constants.ENUM, []);
        let choice = null;

        if (!_.isEmpty(enumOptions)) {
            choice = _.sample(enumOptions);
        }

        return choice;
    },

    getRange: function(config) {
        let minimum = _.get(config, constants.MINIMUM, 1);
        let maximum = _.get(config, constants.MAXIMUM, LIMIT);

        if (_.get(config, constants.MIN_EXCLUDE, false)) {
            minimum += 1;
        }

        if (_.get(config, constants.MAX_EXCLUDE, false)) {
            maximum -= 1;
        }

        if (minimum > maximum) {
            throw new InvalidDataOptionsError(`Minimum cannot be lower than maximum - ${JSON.stringify(config)}`);
        }

        return [minimum, maximum];
    }

};


class ResourceProvider {
    constructor(resourceName, dbResourceProviderInstance) {
        this.resourceName = resourceName;
        this.dbResourceProviderInstance = dbResourceProviderInstance;
    }

    /*
    Options Available are:
        - delete: Whether to delete this resource while fetching. Default: false
        - items: Number of items to fetch. default: 1. Is always 1 for delete: true
        - first: If number of items are 1, return primitive instead of array. Default: true
    */
    static getOptions(options) {

        if(_.isNil(options)) {
            options = {};
        }

        if (_.isNil(options.items)) {
            options.items = 1;
        }

        if (_.isNil(options.delete)) {
            options.delete = false;
        }

        if (options.delete) {
            options.items = 1;
        }

        if (_.isNil(options.flatForSingle)) {
            options.flatForSingle = options.items === 1;
        }

        return options;
    }

    getResources(profile, options) {

        options = ResourceProvider.getOptions(options);

        // Several Lodash arguments work only on arrays, so converting here if set
        let resources = [...this.dbResourceProviderInstance.getResource(profile, this.resourceName, options)];

        if (_.isEmpty(resources)) {
            throw new EmptyResourceError(`Resource Pool not found for ${this.resourceName}`);
        }

        return options.flatForSingle ? resources[0] : resources;
    }

}


class Provider {
    /*
        This class is responsible for generating data for given schema.
        Data generation may be done from DB cache or from fake methods
     */

    constructor(profile=null) {
        this.profile = profile;
        this.dbResourceProviderInstance = Resource.instance;

        this.configResourceMap = {};
        this.relatedResourceData = {};
    }

    reset() {
        this.configResourceMap = {};
        this.relatedResourceData = {};
    }

    static getFakeData(config) {
        const fakeFunc = FakeData.getFakeMapper(config);

        let ret = null;

        if (fakeFunc) {
            ret = fakeFunc(config);
        }

        return ret;
    }

    getResource(resource, options) {
        const resourceProvider = new ResourceProvider(resource, this.dbResourceProviderInstance);
        const independentResourceValue = resourceProvider.getResources(this.profile, options);
        let resourceValue = this.relatedResourceData[resource];

        if (_.isUndefined(resourceValue)) {
            resourceValue = independentResourceValue;
        }

        this.configResourceMap[resource] = new Set(_.isArray(resourceValue) ? resourceValue: [resourceValue]);
        return resourceValue;
    }

    itemResolution(config) {
        const resource = _.get(config, constants.RESOURCE);
        let retValue;

        if (resource) {
            retValue = this.getResource(resource, config.options);
        } else {
            let itemType = _.get(config, constants.TYPE);

            if (!itemType) {
                throw new InvalidDataOptionsError(`Item type must be defined - ${JSON.stringify(config)}`);
            }

            if (itemType === constants.ARRAY) {
                retValue = this.resolveArray(config);
            } else if (itemType === constants.OBJECT) {
                retValue = this.resolveObject(config);
            } else {
                retValue = Provider.getFakeData(config);
            }
        }

        return retValue;

    }

    getRelatedResources(resources) {

        const self = this;

        if (!_.isEmpty(resources)) {
            let resourceValueMap = relatedResources.query(resources, this.profile);

            let validMap = _.filter(resourceValueMap, singleMap => {
                return _.every(singleMap, (value, key) => {
                    return self.dbResourceProviderInstance.doesExist(self.profile, key, value);
                });
            });

            self.relatedResourceData =  _.sample(validMap) || {};
        }
    }

    resolveArray(config) {
        const itemConfig = _.get(config, constants.ITEMS);
        const self = this;

        if (_.isEmpty(itemConfig)) {
            throw new InvalidDataOptionsError(`Items should be defined for Array type - ${JSON.stringify(itemConfig)}`)
        }

        const minItems = _.get(config, constants.MIN_ITEMS, 0);
        const maxItems = _.get(config, constants.MAX_ITEMS, Math.max(10, minItems + 1));

        let items = _.range(_.random(minItems, maxItems)).map(() => self.itemResolution(itemConfig));

        if (_.get(config, constants.UNIQUE_ITEMS, false)) {
            items = new Set(items);
            // If due to de-duplication, our array count decreases and is less than what is required
            while (items.length < minItems){
                items.add(self.itemResolution(itemConfig));
            }
            items = Array.from(items);
        }
        return items;
    }

    resolveObject(config) {

        // Short-circuit return if Type is Array
        let itemType = _.get(config, constants.TYPE);
        if (itemType === constants.ARRAY) {
            return this.resolveArray(config);
        }

        // We want to respect empty properties and additional properties
        let properties = config[constants.PROPERTIES];
        let additionalProperties = config[constants.ADDITIONAL_PROPERTIES];
        const self = this;

        if(!properties && !additionalProperties) {
            // This may be manual, so try treating whole object as properties
            properties = {};
            _.forEach(config, function(value, key) {
                if (typeof value === "object") {
                    properties[key] = value;
                }
            })
        }

        if (!properties) {
            properties = {};
        }

        if (!additionalProperties) {
            additionalProperties = {};
        }

        let dataObject = {};

        _.forEach(properties, function(propConfig, name) {
            const itemValue = self.itemResolution(propConfig);
            if (!_.isNil(itemValue)) {
                dataObject[name] = itemValue;
            }
        });

        if (!_.isEmpty(additionalProperties)) {
            const addPropMapper = self.itemResolution(additionalProperties);
            if (addPropMapper) {
                // Generate minimum possible additional properties
                _.forEach(_.range(_.get(additionalProperties, constants.MIN_PROPERTIES, 0)), function (index) {
                    dataObject["artillery_load_test_" + index] = addPropMapper;
                });
            }
        }

        return dataObject;
    }
}


class ResponseDataParser {
    /*
        This class is responsible for parsing responses and updating cached DB as per response
     */

    constructor(profile=null) {
        this.profile = profile;
        this.dbResourceInstance = Resource.instance;
        this.resourceMap = {};
    }

    parseArray(schema, response) {

        const self = this;

        if (_.isEmpty(response)) {
            return;     // Short-circuit return
        }

        if (typeof response[0] === "object") {
            let itemConfig = _.get(schema, constants.ITEMS, {});
            // Run the Parser for first 10 values, which should be sufficient
            _.forEach(_.slice(response, 0, 10), function (value) {
                self.parser(_.get(itemConfig, constants.PROPERTIES, itemConfig), value);
            });
        } else {
            let resource = _.get(schema, constants.RESOURCE);

            if (!_.isNil(resource)) {
                self.addData(resource, response);
            }
        }
    }

    parseObject(schema, response) {

        const self = this;

        _.forEach(schema, function (schemaConfig, key) {

            if (_.isNil(response[key])) {
                return;     // Short-circuit return
            }

            if (_.isArray(response[key])) {
                self.parseArray(schemaConfig, response[key]);
            } else if (typeof schemaConfig === "object" && schemaConfig.constructor === Object) {
                // First check if resource is available
                let resource = _.get(schemaConfig, constants.RESOURCE);
                if (!_.isNil(resource)) {
                    self.addData(resource, response[key]);
                } else if (typeof response[key] === "object" && response[key].constructor === Object){
                    // Expect that if Response has objects, then schema would have object
                    // It is much faster than checking each properties in schema
                    self.parser(schemaConfig, response[key]);
                }
            }
        });
    }

    /*
        Entry Point for this class.
     */
    resolve(schema, response, reqResourceMap) {
        // Initialize with resource Map of request
        this.resourceMap = reqResourceMap || {};

        this.parser(schema, response);

        if (!_.isEmpty(this.resourceMap)) {
            relatedResources.insert(this.resourceMap, this.profile);
        }

        // Reset the resource Map
        this.resourceMap = {};

        return true;
    }

    parser(schema, response) {

        if (_.isArray(response)) {
            this.parseArray(schema, response);
        } else {
            this.parseObject(schema, response);
        }
    }

    addData(resourceKey, values) {
        const newResources = new Set(_.isArray(values) ? values: [values]);

        if (!_.isEmpty(newResources))
        {
            this.resourceMap[resourceKey] = newResources;
            if(!settings.NOT_UPDATE_RUN_TIME_RESOURCES.has(resourceKey)) {
                this.dbResourceInstance.updateResource(this.profile, resourceKey, newResources);
            }
        }
    }

    deleteData(resourceKey, resourceValue) {
        this.dbResourceInstance.deleteResource(this.profile, resourceKey, resourceValue);
        return true;
    }

}


module.exports = {
    Provider: Provider,
    ResponseDataParser: ResponseDataParser
};
