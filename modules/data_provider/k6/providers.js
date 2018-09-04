import * as _ from 'js_libs/lodash.js';
import * as faker from 'js_libs/faker.js'
import * as yaml from 'js_libs/yaml.js'

import * as constants from 'js_libs/constants.js'
import * as settings from 'js_libs/settings.js'

/*
        Custom Exception Definitions
 */

class InvalidDataOptionsError extends Error {}

class EmptyResourceError extends Error {}

/*
    End Exceptions Definition
 */

const LIMIT = Math.pow(10, 6);
const MILLISECONDS_IN_YEAR = 86400 * 365.25 * 1000;     // Seconds in day * avg. number of days in years * ms in sec


const FakeData = {

    getFakeMapper: function(config) {

        const itemType = _.get(config, constants.TYPE);

        if (!itemType) {
            new InvalidDataOptionsError("Item type must be defined");
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
        MAP[[constants.STRING, constants.UUID]] = FakeData.getUUID;
        MAP[[constants.BOOLEAN, null]] = FakeData.getBoolean;
        MAP[[constants.ARRAY, null]] = FakeData.getArray;
        MAP[[constants.OBJECT, null]] = FakeData.getObject;

        return MAP;
    },

    getInteger: function(config) {
        return FakeData.getEnum(config) ||
            _.random(...FakeData.getRange(config)) * _.get(config, constants.MULTIPLE_OF, 1);
    },

    getFloat: function(config) {
        // Short-circuit return
        const num = FakeData.getEnum(config);
        if (num) {
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
        return FakeData.getEnum(config) ||
            faker.lorem.text(FakeData.getOptions(config)["maximum"])
    },

    getDate: function(config) {
        const date = FakeData.getRandomDateTime(config);
        return `${date.getUTCFullYear()}-${("0" + (date.getUTCMonth() + 1)).slice(-2)}-${("0" + date.getUTCDate()).slice(-2)}`;
    },

    getDateTime: function(config) {
        return FakeData.getRandomDateTime(config).toISOString();
    },

    getPassword: function(config) {
        return FakeData.getEnum(config) || faker.internet.password(FakeData.getOptions(config)["maximum"]);
    },

    getBase64: function(config) {
        return btoa(FakeData.getString(config));
    },

    getEmail: function(config) {
        return FakeData.getEnum(config) || faker.internet.email();
    },

    getUUID: function(config) {
        return faker.random.uuid();
    },

    getBoolean: function(config) {
        return faker.random.boolean();
    },

    getArray: function(config) {
        const itemConfig = _.get(config, constants.ITEMS);

        if (_.isEmpty(itemConfig)) {
            new InvalidDataOptionsError(`Items should be defined for Array type - ${itemConfig}`)
        }

        const fakeFunc = FakeData.getFakeMapper(itemConfig);

        const minItems = _.get(config, constants.MIN_ITEMS, 0);
        const maxItems = _.get(config, constants.MAX_ITEMS, Math.max(10, minItems + 1));

        let fakeItems = _.range(_.random(minItems, maxItems)).map(_ => fakeFunc(itemConfig));

        if (_.get(config, constants.UNIQUE_ITEMS, false)) {
            fakeItems = new Set(fakeItems);

            // If due to de-duplication, our array count decreases and is less than what is required
            while (fakeItems.length < minItems){
                fakeItems.add(fakeFunc(itemConfig))
            }

            fakeItems = Array.from(fakeItems)
        }

        return fakeItems
    },

    getObject: function(config) {
        const properties = _.get(config, constants.PROPERTIES, {});

        if(_.isEmpty(properties)) {
            new InvalidDataOptionsError(`"Properties should be defined for Object - ${config}`)
        }

        let fakeObject = {};

        _.forEach(properties, function(propConfig, name) {
            const fakeFunc = FakeData.getFakeMapper(propConfig);
            if (fakeFunc) {
                fakeObject[name] = fakeFunc(propConfig);
            }
        });

        return fakeObject
    },

    getRandomDateTime: function(config) {
        // Date time between 30 years in past to 30 years in future (approx.)
        const now = _.now();
        const start = now - MILLISECONDS_IN_YEAR * 30;
        const end = now + MILLISECONDS_IN_YEAR * 30;
        return new Date(_.random(start, end));
    },

    getOptions: function(config) {
        /*
        Swagger supports following options:
            - MinLength
            - MaxLength
            - Pattern

        We are only supporting MaxLength for now, and even then, always generating string of maxLength Char always
        */

        return {
            "maximum": _.get(config, constants.MAX_LENGTH, 100)   // Arbitrarily set max length
        };
    },

    getEnum: function(config) {
        const enumOptions = _.get(config, constants.ENUM, []);
        let choice = null;

        if (!_.isEmpty(enumOptions)) {
            choice = _.sample(enumOptions)
        }

        return choice
    },

    getRange: function(config) {
        let minimum = _.get(config, constants.MINIMUM, -LIMIT);
        let maximum = _.get(config, constants.MAXIMUM, LIMIT);

        if (_.get(config, constants.MIN_EXCLUDE, false)) {
            minimum += 1;
        }

        if (_.get(config, constants.MAX_EXCLUDE, false)) {
            maximum -= 1;
        }

        if (minimum > maximum) {
            new InvalidDataOptionsError("Minimum cannot be lower than maximum");
        }

        return [minimum, maximum];
    }

};


class ResourceProvider {
    constructor(resourceName, items, isFlatForSingle) {
        this.resourceName = resourceName;
        this.items = items || 1;
        this.isFlat = this.items === 1 ? isFlatForSingle : false;

        this.resources = {};

        this.profiles = ResourceProvider.readYAMLFile(settings.PROFILES_FILE);
        this.activeProfile = null;
    }

    get profileResource() {
        return _.get(_.get(this.profiles, this.activeProfile, {}), "resource_file", this.activeProfile + ".yaml")
    }

    static readYAMLFile(relativePath) {
        return yaml.load(relativePath);
    }

    resourceSet() {
        // Several Lodash arguments work only on arrays, so converting here if set
        let resourceSet = [..._.get(this.resources, this.resourceName, [])];

        if (resourceSet.length > self.items) {
            resourceSet = _.sampleSize(resourceSet, self.items);
        }

        return resourceSet;
    }

    getResources(profile) {
        this.activeProfile = profile;

        // Not able to find a short and good module in JS which can work with any OS
        // So this will only work with OS which use / as path separator
        this.resources = ResourceProvider.readYAMLFile(settings.RESOURCES_FOLDER + "/" + this.profileResource);

        let resources = this.resourceSet();

        if (_.isEmpty(resources)) {
            new EmptyResourceError(`Resource Pool not found for ${this.resourceName}`);
        }

        if (this.isFlat) {
            resources = resources[0];
        }

        return resources;
    }
}


export class Provider {

    constructor(profile=null) {
        this.profile = profile;
    }

    static getFakeData(config) {
        const fakeFunc = FakeData.getFakeMapper(config);

        let ret = null;

        if (fakeFunc) {
            ret = fakeFunc(config);
        }

        return ret;
    }

    getResource(resource) {
        const resourceProvider = new ResourceProvider(resource);
        return resourceProvider.getResources(this.profile);
    }

    generateData(config) {

        let dataBody = {};
        const self = this;

        _.forEach(config, function(itemConfig, itemName) {

            const resource = _.get(itemConfig, constants.RESOURCE);

            let value = resource ? self.getResource(resource) : Provider.getFakeData(itemConfig);

            if (value) {
                dataBody[itemName] = value;
            }
        });

        return dataBody;
    }
}
