const fs = require('fs');
const path = require("path");

RandExp = require("randexp");
faker = require("faker");
_ = require("lodash");

const exceptions = require('./exceptions');
const constants = require('./constants');
const settings = require('./settings');

const InvalidDataOptionsError = exceptions.InvalidDataOptionsError;
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
        MAP[[constants.FILE, null]] = FakeData.getFile;
        MAP[[constants.FILE, "$any"]] = FakeData.getFile;
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
            const multipleOf = _.get(config, constants.MULTIPLE_OF, 1);
            let [low, high] = FakeData.getRange(config);

            // This is the best way I can come up with,
            // which solves problem of generating a number which is multiple of multipleOf and is within [low, high]
            // We generate a number between [low/multipleOf, high/multipleOf] and then multiply that by multipleOf
            low = Math.ceil(low / multipleOf);
            high = Math.floor(high / multipleOf);

            value = multipleOf * _.random(low, high);
        }

        return value;
    },

    getFloat: function(config) {
        // Short-circuit return
        const num = FakeData.getEnum(config);
        if (!_.isNull(num)) {
            return num;
        }

        let [minimum, maximum] = FakeData.getRange(config);
        const leftSide = _.random(minimum, maximum);
        const rightSide = +Math.random().toFixed(2);        // Plus to convert it back into integer

        let finalNumber = leftSide + rightSide;

        if (finalNumber > maximum) {
            finalNumber = +maximum.toFixed(2);
        }

        return finalNumber;
    },

    getFile: function(config) {

        // Assuming the code is always called from main function.
        // We can definitely change this later to detect script call directory and then try to reach this path
        const basePath = path.join(settings.DIST_FOLDER, settings.DUMMY_FILES_FOLDER);

        // We provide hook methods to over-ride default text file selection
        return fs.createReadStream(path.join(basePath, 'dummy.txt'));
    },

    getString: function(config) {
        let value = FakeData.getEnum(config);

        if (_.isNull(value)) {

            let options = FakeData.getOptions(config);

            if (options.pattern) {
                value = new RandExp(options.pattern).gen()
            } else {
                value = faker.lorem.text().substring(0, options.length);
            }
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
            faker.name.firstName().substring(0, 5).replace(/([\\~#&*{}/:<>?|"'])/ig, '').toLowerCase() +
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
        */

        let max = _.get(config, constants.MAX_LENGTH, 10);
        let min = _.get(config, constants.MIN_LENGTH, 1);

        return {
            // We want to generate a string which is shorter than maximum, but always equal to or exceeding minimum
            "length": Math.max(Math.floor(max/2), min),
            "pattern": config[constants.PATTERN]
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

exports.FakeData = FakeData;
