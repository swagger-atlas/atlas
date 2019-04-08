_ = require('lodash');

const provider = require('../../atlas/modules/data_provider/artillery/providers');
const relatedResources = require('../../atlas/modules/data_provider/artillery/relationResources').relationshipResource;
const Resource = require('../../atlas/modules/data_provider/artillery/resources').Resource;
const constants = require('../constants');
const settings = require('../settings');

jest.mock('../../atlas/modules/data_provider/artillery/relationResources');
jest.mock('../../atlas/modules/data_provider/artillery/resources');

resourceInstanceMock = jest.fn();
Resource.instance = resourceInstanceMock;

const ResponseDataParser = provider.ResponseDataParser;
const respDataParser = new ResponseDataParser("profile");


describe('test resolve', () => {

    let origParser;
    let origFormatter;

    beforeAll(() => {
        relatedResources.insert = jest.fn();
    });

    beforeEach(() => {
        origParser = respDataParser.parser;
        origFormatter = respDataParser.formatResourceMap;
    });

    afterEach(() => {
        respDataParser.parser = origParser;
        respDataParser.formatResourceMap = origFormatter;
        relatedResources.insert.mockClear();
    });

    test('no resource map', () => {
        respDataParser.parser = jest.fn(() => {return {}});

        expect(respDataParser.resolve({"scheme": 1}, {"resp": 1}, {})).toBeTruthy();

        expect(relatedResources.insert).toBeCalledTimes(0);
        expect(respDataParser.parser).toBeCalledWith({"scheme": 1}, {"resp": 1})
    });

    test('existing resource map, and parser does not return resources', () => {
        respDataParser.parser = jest.fn(() => {return {}});
        respDataParser.formatResourceMap = jest.fn(() => {return [1, 2]});

        expect(respDataParser.resolve({"scheme": 1}, {"resp": 1}, {"exists": 1})).toBeTruthy();

        expect(relatedResources.insert.mock.calls).toEqual([[1, "profile"], [2, "profile"]]);
        expect(respDataParser.formatResourceMap).toBeCalledWith({"exists": 1});
    });

    test('existing resource map and parser returns resources', () => {
        respDataParser.parser = jest.fn(() => {return {"a": 1, "b": 2}});
        respDataParser.formatResourceMap = jest.fn(() => {return [1, 2]});

        expect(respDataParser.resolve({"scheme": 1}, {"resp": 1}, {"a": 3, "c": 4})).toBeTruthy();

        expect(relatedResources.insert.mock.calls).toEqual([[1, "profile"], [2, "profile"]]);
        expect(respDataParser.formatResourceMap).toBeCalledWith({"a": 3, "b": 2, "c": 4});
    });
});


describe('parseArray test', () => {

    test('empty response should return empty array', () => {
        expect(respDataParser.parseArray({}, [])).toEqual([]);
    });

    test('a non-object type response with no resource returns empty array', () => {
        const schema = {
            [constants.ITEMS]: {}
        };
        expect(respDataParser.parseArray(schema, ["a", "b", "c"])).toEqual([]);
    });

    test('a non-object type response with resource which is not found returns empty array', () => {
        const origAddData = respDataParser.addData;
        respDataParser.addData = jest.fn(() => new Set([]));

        const schema = {
            [constants.ITEMS]: {
                [constants.TYPE]: constants.STRING,
                [constants.RESOURCE]: "abc"
            }
        };

        expect(respDataParser.parseArray(schema, ["a", "b", "c"])).toEqual([]);
        expect(respDataParser.addData).toHaveBeenCalledWith("abc", ["a", "b", "c"]);

        respDataParser.addData = origAddData;
    });

    test('a non-object type response with resource which is found returns array with resources', () => {
        const origAddData = respDataParser.addData;
        respDataParser.addData = jest.fn(() => new Set([1, 2, 3]));

        const schema = {
            [constants.ITEMS]: {
                [constants.TYPE]: constants.STRING,
                [constants.RESOURCE]: "abc"
            }
        };

        expect(respDataParser.parseArray(schema, ["a", "b", "c"])).toEqual({"abc": new Set([1, 2, 3])});
        expect(respDataParser.addData).toHaveBeenCalledWith("abc", ["a", "b", "c"]);

        respDataParser.addData = origAddData;
    });

    test('object type response calls the parser for maximum of 10 times, and array is returned with result of parser', () => {
        const origParser = respDataParser.parser;
        respDataParser.parser = jest.fn((schema, value) => value.res + 1);

        const schema = {
            [constants.ITEMS]: {
                [constants.PROPERTIES]: {
                    key: "val"
                }
            }
        };
        let inputResponse = [];
        _.forEach(_.range(20), (val) => {
            inputResponse.push({res: val})
        });

        const actualResponse = respDataParser.parseArray(schema, inputResponse);

        let expectedResponse = [];
        _.forEach(_.range(10), (val) => expectedResponse.push(val + 1));   // Note that we only do for 10 values

        expect(actualResponse).toEqual(expectedResponse);
        expect(respDataParser.parser).toBeCalledTimes(10);
        expect(respDataParser.parser).toHaveBeenLastCalledWith({key: "val"}, {res: 9});

        respDataParser.parser = origParser;
    });
});


describe('parser test', () => {

    test('array response triggers parseArray', () => {
        const origParseArray = respDataParser.parseArray;
        respDataParser.parseArray = jest.fn(() => [4, 5, 6]);

        expect(respDataParser.parser({key: "val"}, [1, 2, 3])).toEqual([4, 5, 6]);
        expect(respDataParser.parseArray).toHaveBeenCalledWith({key: "val"}, [1, 2, 3]);

        respDataParser.parseArray = origParseArray;
    });

    test('object response triggers parseObject', () => {
        const origParseObject = respDataParser.parseObject;
        respDataParser.parseObject = jest.fn(() => { return {"a": 1} });

        expect(respDataParser.parser({key: "val"}, {lang: "xp"})).toEqual({"a": 1});
        expect(respDataParser.parseObject).toHaveBeenCalledWith({key: "val"}, {lang: "xp"});

        respDataParser.parseObject = origParseObject;
    });
});


test('deleteData calls delete resource', () => {

    resourceInstanceMock.deleteResource = jest.fn();

    expect(respDataParser.deleteData("key", "value")).toBe(true);
    expect(resourceInstanceMock.deleteResource).toHaveBeenCalledWith("profile", "key", "value");
});


describe('addData test', () => {

    beforeEach(() => {
        resourceInstanceMock.updateResource = jest.fn();
    });

    afterEach(() => {
        resourceInstanceMock.updateResource.mockReset();
    });

    test('values are array in input', () => {
        const resourceSet = new Set(["a", "b"]);
        expect(respDataParser.addData("key", ["a", "b"])).toEqual(resourceSet);
        expect(resourceInstanceMock.updateResource).toHaveBeenCalledWith("profile", "key", resourceSet);
    });

    test('values are not array in input', () => {
        const resourceSet = new Set(["a"]);
        expect(respDataParser.addData("key", "a")).toEqual(resourceSet);
        expect(resourceInstanceMock.updateResource).toHaveBeenCalledWith("profile", "key", resourceSet);
    });

    test('empty input values return empty output', () => {
        const resourceSet = new Set([]);
        expect(respDataParser.addData("key", [])).toEqual(resourceSet);
        expect(resourceInstanceMock.updateResource).not.toBeCalled();
    });

    test('resource key is set to be not updated at run time', () => {
        const resourceSet = new Set(["a"]);
        expect(respDataParser.addData("random_key", ["a"])).toEqual(resourceSet);
        expect(resourceInstanceMock.updateResource).not.toBeCalled();
    });
});
