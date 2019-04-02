const faker = require('faker');
const path = require('path');
const _ = require('lodash');

const fakeProvider = require('../atlas/modules/data_provider/artillery/fakeProvider');
const exceptions = require('../atlas/modules/data_provider/artillery/exceptions');
const constants = require('./constants');
const settings = require('./settings');


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

    test('raises error on invalid config', () => {
        expect(() => fakeData.getInteger({
            [constants.MAXIMUM]: 5,
            [constants.MINIMUM]: 10
        })).toThrow(InvalidDataOptionsError);
    });

    test('return value within minimum and maximum', () => {
        expect(fakeData.getInteger({
            [constants.MAXIMUM]: 15,
            [constants.MINIMUM]: 10
        })).inBetween(10, 15);
    });

    test('return value within minimum and maximum with min exclusive', () => {
        expect(fakeData.getInteger({
            [constants.ENUM]: [],
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


describe('getDate test cases', () => {

    let originalRandomDateTime;

    beforeAll(() => {
        originalRandomDateTime = fakeData.getRandomDateTime;
    });

    afterAll(() => {
        fakeData.getRandomDateTime = originalRandomDateTime;
    });

    test('getDate returns date in correct format', () => {
        fakeData.getRandomDateTime = jest.fn(() => new Date('2000-01-01T01:00:00Z'));
        expect(fakeData.getDate()).toBe("2000-01-01");
    });

    test('getDate returns date without pads', () => {
        fakeData.getRandomDateTime = jest.fn(() => new Date('2000-10-10T01:00:00Z'));
        expect(fakeData.getDate()).toBe("2000-10-10");
    });
});


describe('getDateTime test cases', () => {

    let originalRandomDateTime;

    beforeAll(() => {
        originalRandomDateTime = fakeData.getRandomDateTime;
    });

    afterAll(() => {
        fakeData.getRandomDateTime = originalRandomDateTime;
    });

    test('getDateTime returns date-time in correct format', () => {
        fakeData.getRandomDateTime = jest.fn(() => new Date('2000-01-01T01:00:00Z'));
        expect(fakeData.getDateTime()).toBe("2000-01-01T01:00:00.000Z");
    });
});


describe('getURI test cases', () => {

    test('getURI returns avatar', () => {
        faker.internet.avatar = jest.fn(() => "https://abcd.com");
        expect(fakeData.getURI({})).toBe("https://abcd.com");
        faker.internet.avatar.mockReset();
    });
});


describe('getURL test cases', () => {

    test('getURL returns url', () => {
        faker.internet.protocol = jest.fn(() => "https");
        faker.name.firstName = jest.fn(() => "google");
        faker.internet.domainSuffix = jest.fn(() => "com");

        expect(fakeData.getURL({})).toBe("https://googl.com");

        faker.internet.protocol.mockReset();
        faker.name.firstName.mockReset();
        faker.internet.domainSuffix.mockReset();
    });
});


describe('getSlug test cases', () => {

    test('getSlug returns slug', () => {
        faker.internet.userName = jest.fn(() => "abc xyz.com be$at");

        expect(fakeData.getSlug({})).toBe("abc-xyz.com-beat");

        faker.internet.userName.mockReset();
    });
});


describe('getPassword test cases', () => {

    test('for enum, return value from enum', () => {
        expect(fakeData.getPassword({
            [constants.ENUM]: ["abc", "xyz"],
        })).in(["abc", "xyz"]);
    });

    test('generate password for normal config', () => {
        faker.internet.password = jest.fn(() => "password");

        expect(fakeData.getPassword({})).toBe("password");

        faker.internet.userName.mockReset();
    });
});


describe('getBase64 test cases', () => {

    test('getBase64 returns base64 string', () => {
        fakeData.getString = jest.fn(() => "a");

        expect(fakeData.getBase64({})).toBe("YQ==");

        fakeData.getString.mockReset();
    });
});


describe('getEmail test cases', () => {

    test('for enum, return value from enum', () => {
        expect(fakeData.getEmail({
            [constants.ENUM]: ["a@a.com", "a@b.com"],
        })).in(["a@a.com", "a@b.com"]);
    });

    test('generate valid email', () => {
        faker.internet.email = jest.fn(() => "a@a.com");

        expect(fakeData.getEmail({})).toBe("a@a.com");

        faker.internet.email.mockReset();
    });
});


describe('getUUID test cases', () => {

    test('getUUID returns uuid', () => {
        faker.random.uuid = jest.fn(() => "abcd-efgh");

        expect(fakeData.getUUID({})).toBe("abcd-efgh");

        faker.random.uuid.mockReset();
    });
});


describe('getBoolean test cases', () => {

    test('getUUID returns uuid', () => {
        expect(fakeData.getBoolean({})).in([true, false]);
    });
});


describe('getRandomDateTime test cases', () => {

    const MILLISECONDS_IN_YEAR = 86400 * 365.25 * 1000;

    test('get date in the the range', () => {
        const now = _.now();
        _.now = jest.fn(() => now);

        const date = fakeData.getRandomDateTime();

        expect(date).isInstance(Date);
        expect(date.getTime()).inBetween(now, now + MILLISECONDS_IN_YEAR);

        _.now.mockReset();
    })
});


describe('getFile test cases', () => {
    test('getFile returns Stream', () => {
        const fs = require('fs');

        const origReadStream = fs.createReadStream;
        fs.createReadStream = jest.fn();

        fakeData.getFile();

        expect(fs.createReadStream).toHaveBeenCalledWith(
            path.join(settings.DIST_FOLDER, settings.DUMMY_FILES_FOLDER, 'dummy.txt')
        );

        fs.createReadStream = origReadStream;

    });
});
