const fakeProvider = require('../../atlas/modules/data_provider/artillery/fakeProvider');
const exceptions = require('../../atlas/modules/data_provider/artillery/exceptions');
const constants = require('../constants');


const fakeData = fakeProvider.FakeData;
const InvalidDataOptionsError = exceptions.InvalidDataOptionsError;
const LIMIT = Math.pow(10, 2);


describe('get fake mapper test cases', () => {

    test('no type raises error', () => {
        expect(() => {
            fakeData.getFakeMapper({[constants.TYPE]: ""})
        }).toThrow(InvalidDataOptionsError);
    });

    test('string type and format date should return date Func', () => {
        expect(fakeData.getFakeMapper({
            [constants.TYPE]: constants.STRING,
            [constants.FORMAT]: constants.DATE
        })).toEqual(fakeData.getDate);
    });

    test('integer type with invalid format should return getInteger func', () => {
        expect(fakeData.getFakeMapper({
            [constants.TYPE]: constants.INTEGER,
            [constants.FORMAT]: constants.DATE
        })).toEqual(fakeData.getInteger);
    });

});


describe('getInteger Test cases', () => {

    test('for enum, return value from enum', () => {
        expect(fakeData.getInteger({
            [constants.ENUM]: [1, 2, 3],
            [constants.MAXIMUM]: 15,
            [constants.MINIMUM]: 10
        })).inBetween(1, 3);
    });

    test('return value within minimum and maximum', () => {
        expect(fakeData.getInteger({
            [constants.MAXIMUM]: 15,
            [constants.MINIMUM]: 10
        })).inBetween(10, 15);
    });

    test('return value within minimum and maximum with min exclusive', () => {
        expect(fakeData.getInteger({
            [constants.MAXIMUM]: 15,
            [constants.MINIMUM]: 10,
            [constants.MIN_EXCLUDE]: true
        })).inBetween(11, 15);
    });

    test('return value within minimum and maximum with max exclusive', () => {
        expect(fakeData.getInteger({
            [constants.MAXIMUM]: 15,
            [constants.MINIMUM]: 10,
            [constants.MAX_EXCLUDE]: true
        })).inBetween(10, 14);
    });

    test('return value within minimum and maximum and a multiple of number', () => {
        expect(fakeData.getInteger({
            [constants.MAXIMUM]: 15,
            [constants.MINIMUM]: 10,
            [constants.MULTIPLE_OF]: 2
        })).in([10, 12, 14]);
    });

    test('minimum is set to 1 if not present', () => {
        expect(fakeData.getInteger({
            [constants.MAXIMUM]: 15,
        })).inBetween(1, 15);
    });

    test('maximum is set to LIMIT if not present', () => {
        expect(fakeData.getInteger({
            [constants.MINIMUM]: 10,
        })).inBetween(10, LIMIT);
    });

    test('0 in enum returns 0', () => {
        expect(fakeData.getInteger({
            [constants.ENUM]: [0],
            [constants.MAXIMUM]: 15,
            [constants.MINIMUM]: 10
        })).toEqual(0);
    });

});


describe('getFloat Test cases', () => {

    test('for enum, return value from enum', () => {
        expect(fakeData.getFloat({
            [constants.ENUM]: [1.0, 2.0, 3.0],
            [constants.MAXIMUM]: 15.0,
            [constants.MINIMUM]: 10.0
        })).inBetween(1.0, 3.0);
    });

    test('return value within minimum and maximum', () => {
        expect(fakeData.getFloat({
            [constants.MAXIMUM]: 15.0,
            [constants.MINIMUM]: 10.0
        })).inBetween(10.0, 15.0);
    });

    test('return value within minimum and maximum with min exclusive', () => {
        expect(fakeData.getFloat({
            [constants.MAXIMUM]: 15.0,
            [constants.MINIMUM]: 10.0,
            [constants.MIN_EXCLUDE]: true
        })).inBetween(11.0, 15.0);
    });

    test('return value within minimum and maximum with max exclusive', () => {
        expect(fakeData.getFloat({
            [constants.MAXIMUM]: 15.0,
            [constants.MINIMUM]: 10.0,
            [constants.MAX_EXCLUDE]: true
        })).inBetween(10.0, 14.0);
    });

    test('minimum is set to 1 if not present', () => {
        expect(fakeData.getFloat({
            [constants.MAXIMUM]: 15.0
        })).inBetween(1.0, 15.0);
    });

    test('maximum is set to LIMIT if not present', () => {
        expect(fakeData.getFloat({
            [constants.MINIMUM]: 10.0
        })).inBetween(10.0, LIMIT);
    });

    test('value is set to maximum if random exceeds maximum', () => {
        expect(fakeData.getFloat({
            [constants.MAXIMUM]: 10.1,
            [constants.MINIMUM]: 10.0
        })).inBetween(10.0, 10.1);
    });

    test('0 in enum returns 0', () => {
        expect(fakeData.getInteger({
            [constants.ENUM]: [0.0],
            [constants.MAXIMUM]: 15.0,
            [constants.MINIMUM]: 10.0
        })).toEqual(0.0);
    });

});


describe('getStringJSON test cases', () => {
    test('returns empty object', () => {
        expect(fakeData.getStringJSON()).toEqual({});
    });
});


describe('getString test cases', () => {

    test('for enum, return value from enum', () => {
        expect(fakeData.getString({
            [constants.ENUM]: ["a", "b"],
            [constants.MAX_LENGTH]: 4,
            [constants.MIN_LENGTH]: 2
        })).in(["a", "b"]);
    });

    test('empty string in enum returns empty string', () => {
        expect(fakeData.getString({
            [constants.ENUM]: [""],
            [constants.MAX_LENGTH]: 4,
            [constants.MIN_LENGTH]: 2
        })).toEqual("");
    });

    test('string generates random chars between min and max length', () => {
        expect(fakeData.getString({
            [constants.MAX_LENGTH]: 4,
            [constants.MIN_LENGTH]: 2
        }).length).inBetween(2, 4);
    });

    test('string generated from regex pattern', () => {
        expect(fakeData.getString({
            [constants.PATTERN]: 'ab?c',
        })).in(['abc', 'ac']);
    });

});
