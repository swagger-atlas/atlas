import _ from 'js_libs/lodash.js';
import faker from 'js_libs/faker.js'

import * as constants from 'js_libs/constants.js'
import { Resource } from './resources.js'

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
        MAP[[constants.STRING, constants.SLUG]] = FakeData.getSlug;
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
            faker.lorem.text().slice(0, [FakeData.getOptions(config)["maximum"]])
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

    getSlug: function(config) {
        return faker.helpers.slugify(faker.internet.userName());
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
            throw new InvalidDataOptionsError(`Items should be defined for Array type - ${JSON.stringify(itemConfig)}`)
        }

        const fakeFunc = FakeData.getFakeMapper(itemConfig);

        const minItems = _.get(config, constants.MIN_ITEMS, 0);
        const maxItems = _.get(config, constants.MAX_ITEMS, Math.max(10, minItems + 1));

        let fakeItems = _.range(_.random(minItems, maxItems)).map(() => fakeFunc(itemConfig));

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
            throw new InvalidDataOptionsError(`"Properties should be defined for Object - ${JSON.stringify(config)}`)
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
        let minimum = _.get(config, constants.MINIMUM, 0);
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
    constructor(resourceName, resourceInstance, items, isFlatForSingle) {
        this.resourceName = resourceName;
        this.items = items || 1;
        this.isFlat = this.items === 1 ? isFlatForSingle : false;

        this.resources = {};
        this.resourceInstance = resourceInstance;
    }

    resourceSet() {
        // Several Lodash arguments work only on arrays, so converting here if set
        let resourceSet = [..._.get(this.resources, this.resourceName, [])];

        if (resourceSet.length > this.items) {
            resourceSet = _.sampleSize(resourceSet, this.items);
        }

        return resourceSet;
    }

    getResources(profile) {

        this.resources = _.get(this.resourceInstance.resources, profile, {});

        let resources = this.resourceSet();

        if (_.isEmpty(resources)) {
            throw new EmptyResourceError(`Resource Pool not found for ${this.resourceName}`);
        }

        if (this.isFlat) {
            resources = resources[0];
        }

        return resources;
    }

    addResources(profile, resourceValues) {
        const resources = _.get(this.resourceInstance.resources, profile, {});
        let resourceValue;
        if (resources[this.resourceName] && !_.isEmpty(resources[this.resourceName])) {
            resourceValue = new Set([...resources[this.resourceName], ...resourceValues]);
        } else {
            resourceValue = resourceValues;
        }
        this.resourceInstance.updateResource(profile, this.resourceName, resourceValue);
    }
}


export class Provider {

    constructor(profile=null) {
        this.profile = profile;
        // Ideally, Resource class should be singleton
        // But here we know that Provider would be initialized only once
        this.resourceInstance = new Resource();
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
        const resourceProvider = new ResourceProvider(resource, this.resourceInstance);
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

    addData(config, resourceKey, resourceField) {

        let self = this;

        let newResources = new Set();
        if (_.isArray(config)) {
            _.forEach(config, function (elementConfig) {
                const extractedData = self.extractData(elementConfig, resourceField);
                if (extractedData) {
                    newResources = [...newResources, ...extractedData];
                }
            });
        } else {
            newResources = self.extractData(config, resourceField);
        }

        if (!_.isEmpty(newResources)) {
            new ResourceProvider(resourceKey, self.resourceInstance).addResources(self.profile, newResources);
        }

        return true;
    }

    extractData(config, resourceField) {
        let ret = new Set();
        _.forEach(config, function (itemConfig, itemName) {
            if (itemName === resourceField) {
                if (_.isArray(itemConfig)) {
                    if (!_.isEmpty(itemConfig)) {
                        ret = new Set(itemConfig)
                    }
                } else {
                    if (itemConfig) {
                        ret.add(itemConfig);
                    }
                }
            }
        });
        return ret;
    }
}