import * as _ from 'js_libs/lodash.js';
import * as constants from 'js_libs/constants.js'


const LIMIT = Math.pow(10, 6);

class FakeData {

    getFakeMapper(config) {

        const itemType = _.get(config, constants.TYPE);

        if (!itemType) {
            console.exception("Item type must be defined");
        }

        const itemFormat = _.get(config, constants.FORMAT);

        let fakeFunc = this.FAKE_MAP[[itemType, itemFormat]];

        // If it did not match, try to match any format
        if (!fakeFunc)
            fakeFunc = this.FAKE_MAP[[itemType, "$any"]];

        return fakeFunc
    }

    get FAKE_MAP() {
        // (Type, format) --> function. None should match to no format. any accepts any format at all
        let MAP = {};

        // Defined one by one instead of one go since we want to use composite keys
        MAP[[constants.INTEGER, null]] = "getInteger";
        return MAP;
    }

    getInteger(config) {
        return FakeData.getRandomInt(...FakeData.getRange(config));
    }

    static getRandomInt(min, max) {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min + 1)) + min; //Both inclusive
    }

    static getRange(config) {
        let minimum = _.get(config, constants.MINIMUM, -LIMIT);
        let maximum = _.get(config, constants.MAXIMUM, LIMIT);

        if (_.get(config, constants.MIN_EXCLUDE, false)) {
            minimum += 1;
        }

        if (_.get(config, constants.MAX_EXCLUDE, false)) {
            maximum -= 1;
        }

        if (minimum > maximum) {
            console.exception("Minimum cannot be lower than maximum")
        }

        return [minimum, maximum];
    }

}


export class Provider {

     static getFakeData(config) {
        let genClass = new FakeData();
        const fakeFunc = genClass.getFakeMapper(config);

        let ret = null;

        if (fakeFunc) {
            ret = genClass[fakeFunc](config);
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
