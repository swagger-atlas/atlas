import * as _ from 'js_libs/lodash.js';
import * as constants from 'js_libs/constants.js'
import * as faker from 'js_libs/faker.js'
import { DateTime } from 'js_libs/luxon.js'


/*
        Custom Exception Definitions
 */
class CustomError extends Error {
    constructor(...args) {
        super(...args);
        Error.captureStackTrace(this, CustomError);
    }
}

class InvalidDataOptionsError extends CustomError {}

/*
    End Exceptions Definition
 */

const LIMIT = Math.pow(10, 6);


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
        // https://moment.github.io/luxon/docs/manual/formatting.html#table-of-tokens
        return FakeData.getRandomDateTime(config).toFormat("yyyy-MM-dd");
    },

    getDateTime: function(config) {
        return FakeData.getRandomDateTime(config).toISO();
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
            while (len(fakeItems) < minItems){
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
        // #Date time between 30 years in past to 30 years in future
        const now = DateTime.utc();
        const start = now.plus({years: -30}).toMillis();
        const end = now.plus({years: 30}).toMillis();
        return DateTime.fromMillis(start + Math.random() * (end - start), {zone: 'utc'});
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


export class Provider {

     static getFakeData(config) {
        const fakeFunc = FakeData.getFakeMapper(config);

        let ret = null;

        if (fakeFunc) {
            ret = fakeFunc(config);
        }

        return ret;
    }

    generateData(config) {

        let dataBody = {};

        _.forEach(config, function(itemConfig, itemName) {
           let value = Provider.getFakeData(itemConfig);

           if (value) {
               dataBody[itemName] = value;
           }
        });

        return dataBody;
    }
}
