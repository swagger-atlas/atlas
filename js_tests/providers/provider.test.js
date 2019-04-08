resourceProvider = require('../../atlas/modules/data_provider/artillery/resourceProvider');
fakeProvider = require('../../atlas/modules/data_provider/artillery/fakeProvider');
provider = require('../../atlas/modules/data_provider/artillery/providers');
exceptions = require('../../atlas/modules/data_provider/artillery/exceptions');
relationResources = require('../../atlas/modules/data_provider/artillery/relationResources');
resource = require('../../atlas/modules/data_provider/artillery/resources');
constants = require('../constants');

jest.mock('../../atlas/modules/data_provider/artillery/resourceProvider');
jest.mock('../../atlas/modules/data_provider/artillery/fakeProvider');
jest.mock('../../atlas/modules/data_provider/artillery/relationResources');
jest.mock('../../atlas/modules/data_provider/artillery/resources');

const Provider = provider.Provider;
const Resource = resource.Resource;

resourceInstanceMock = jest.fn();
Resource.instance = resourceInstanceMock;

const providerInstance  = new Provider("profile");
const ResourceProvider = resourceProvider.ResourceProvider;
const FakeData = fakeProvider.FakeData;
const InvalidDataOptionsError = exceptions.InvalidDataOptionsError;
const relatedResources = relationResources.relationshipResource;


describe('roll back delete', function () {

    test('calls resource provider restore func with correct arguments', () => {

        const restoreResourceMock = jest.fn();
        ResourceProvider.mockImplementationOnce(() => {
            return {
                restoreResource: restoreResourceMock
            }
        });

        providerInstance.rollBackDelete("resource", "value");

        expect(restoreResourceMock).toHaveBeenCalledWith("profile", "value");
    });
});


describe('getFakeData tests', () => {

        test('null is returned if there is no fake function', () => {

            FakeData.getFakeMapper = jest.fn(() => null);

            expect(Provider.getFakeData({})).toBeNull();
            expect(FakeData.getFakeMapper).toHaveBeenCalledWith({});
        });

        test('faker is called when we get fake function', () => {

            const fakeFunc = jest.fn(() => 5);
            FakeData.getFakeMapper = jest.fn(() => fakeFunc);

            expect(Provider.getFakeData({})).toBe(5);
            expect(FakeData.getFakeMapper).toHaveBeenCalledWith({});
            expect(fakeFunc).toBeCalledWith({});
        });
    });


test('reset func resets data structures', () => {
    providerInstance.relatedResourceData = {"a": 1, "b": 2};
    providerInstance.configResourceMap = {"a": 1, "b": 2};

    providerInstance.reset();

    expect(providerInstance.relatedResourceData).toEqual({});
    expect(providerInstance.configResourceMap).toEqual({});
});


describe('getResource test cases', () => {

    afterEach(() => {
        providerInstance.reset();
    });

    test('data exists in related resources', () => {
        providerInstance.relatedResourceData = {"a": "relation"};

        const getResourcesMock = jest.fn(() => "independent");
        ResourceProvider.mockImplementationOnce(() => {
            return {
                getResources: getResourcesMock
            }
        });

        expect(providerInstance.getResource("a", {key: "val"})).toEqual("relation");
        expect(providerInstance.configResourceMap).toEqual({a: new Set(["relation"])});
        expect(getResourcesMock).toBeCalledWith("profile", {key: "val"})
    });

    test('data do not exist in related resources', () => {
        const getResourcesMock = jest.fn(() => "independent");
        ResourceProvider.mockImplementationOnce(() => {
            return {
                getResources: getResourcesMock
            }
        });

        expect(providerInstance.getResource("a", {key: "val"})).toEqual("independent");
        expect(providerInstance.configResourceMap).toEqual({a: new Set(["independent"])});
        expect(getResourcesMock).toBeCalledWith("profile", {key: "val"})
    });

    test('data is array', () => {
        const getResourcesMock = jest.fn(() => [1, 2, 3]);
        ResourceProvider.mockImplementationOnce(() => {
            return {
                getResources: getResourcesMock
            }
        });

        expect(providerInstance.getResource("a", {key: "val"})).toEqual([1, 2, 3]);
        expect(providerInstance.configResourceMap).toEqual({a: new Set([1, 2, 3])});
        expect(getResourcesMock).toBeCalledWith("profile", {key: "val"})
    });
});


describe('itemResolution test cases', () => {

    test('item is a resource', () => {
        const getResourceOriginal = providerInstance.getResource;
        providerInstance.getResource = jest.fn(() => "abc");

        expect(providerInstance.itemResolution(
            {[constants.RESOURCE]: "a", options: {"x": 1}})
        ).toBe("abc");

        expect(providerInstance.getResource).toBeCalledWith("a", {"x": 1});

        providerInstance.getResource = getResourceOriginal;
    });

    test('item is an array', () => {
        const resolveArrayOriginal = providerInstance.resolveArray;
        providerInstance.resolveArray = jest.fn(() => 8);

        expect(providerInstance.itemResolution(
            {[constants.TYPE]: constants.ARRAY})
        ).toBe(8);

        expect(providerInstance.resolveArray).toBeCalledWith({[constants.TYPE]: constants.ARRAY});

        providerInstance.resolveArray = resolveArrayOriginal;
    });

    test('item is an object', () => {
        const resolveObjectOriginal = providerInstance.resolveObject;
        providerInstance.resolveObject = jest.fn(() => 5);

        expect(providerInstance.itemResolution(
            {[constants.TYPE]: constants.OBJECT})
        ).toBe(5);

        expect(providerInstance.resolveObject).toBeCalledWith({[constants.TYPE]: constants.OBJECT});

        providerInstance.resolveObject = resolveObjectOriginal;
    });

    test('item is normal data', () => {
        const getFakeDataOriginal = Provider.getFakeData;
        Provider.getFakeData = jest.fn(() => 3);

        expect(providerInstance.itemResolution(
            {[constants.TYPE]: "some_type"})
        ).toBe(3);

        expect(Provider.getFakeData).toBeCalledWith({[constants.TYPE]: "some_type"});

        Provider.getFakeData = getFakeDataOriginal;
    });

    test('item is not configured properly', () => {
        expect(() => providerInstance.itemResolution({})).toThrow(InvalidDataOptionsError);
    })
});


describe('getRelatedResources test cases', () => {

    let doesExistMock;

    beforeAll(() => {
        providerInstance.reset();
        const mockResources = {
            a: new Set([1, 2, 3]),
            b: new Set([3, 4])
        };
        doesExistMock = jest.fn((profile, key, value) => {
            return mockResources[key].has(value);
        });
        resourceInstanceMock.doesExist = doesExistMock;
    });

    afterEach(() => {
        providerInstance.reset();
        doesExistMock.mockClear();
    });

    afterAll(() => {
        resourceInstanceMock.mockReset();
    });

    test('empty resource Input does not set related resources', () => {
        providerInstance.getRelatedResources([]);
        expect(providerInstance.relatedResourceData).toEqual({});
    });

    test('no resources found in query, expect no change in relatedResources', () => {
        relatedResources.query = jest.fn(() => []);
        providerInstance.getRelatedResources(["a", "b"]);

        expect(providerInstance.relatedResourceData).toEqual({});
        expect(relatedResources.query).toHaveBeenCalledWith(["a", "b"], "profile");
    });

    test('query returns resources for which some are not found valid', () => {
        relatedResources.query = jest.fn(() => [
            {a: 1, b: 2}, {a: 2, b: 3}
        ]);

        providerInstance.getRelatedResources(["a", "b"]);

        expect(providerInstance.relatedResourceData).toEqual({a: 2, b: 3});
        expect(relatedResources.query).toHaveBeenCalledWith(["a", "b"], "profile");
    });

    test('query returns multiple valid resources, we choose one at random', () => {
        relatedResources.query = jest.fn(() => [
            {a: 3, b: 4}, {a: 2, b: 3}
        ]);

        providerInstance.getRelatedResources(["a", "b"]);

        expect([{a: 2, b: 3}, {a: 3, b: 4}]).toContainEqual(providerInstance.relatedResourceData);
        expect(relatedResources.query).toHaveBeenCalledWith(["a", "b"], "profile");
    });
});


describe('resolveArray test cases', () => {

    const itemResolutionOrig = providerInstance.itemResolution;

    beforeEach(() => {
        providerInstance.itemResolution = jest.fn(() => "a")
    });

    afterEach(() => {
       providerInstance.itemResolution = itemResolutionOrig;
    });

    test('items are not defined', () => {
        expect(() => {
            providerInstance.resolveArray({})
        }).toThrow(InvalidDataOptionsError);
    });

    test('min, max items not defined', () => {

        const min = 0;
        const max = min + 10;

        const items = {
            key: "value"
        };
        const config = {
            [constants.ITEMS]: items
        };
        const received = providerInstance.resolveArray(config);

        expect(received.length).inBetween(min, max);
        expect(providerInstance.itemResolution.mock.calls.length).inBetween(min, max);
    });

    test('min no of items defined, max not defined', () => {

        const min = 5;
        const max = min + 10;

        const items = {
            key: "value"
        };
        const config = {
            [constants.ITEMS]: items,
            [constants.MIN_ITEMS]: min
        };
        const received = providerInstance.resolveArray(config);

        expect(received.length).inBetween(min, max);
        expect(providerInstance.itemResolution.mock.calls.length).inBetween(min, max);
    });

    test('min and max no of items defined', () => {
        const min = 5;
        const max = 8;

        const items = {
            key: "value"
        };
        const config = {
            [constants.ITEMS]: items,
            [constants.MIN_ITEMS]: min,
            [constants.MAX_ITEMS]: max
        };
        const received = providerInstance.resolveArray(config);

        expect(received.length).inBetween(min, max);
        expect(providerInstance.itemResolution.mock.calls.length).inBetween(min, max);
    });

    test('min number not defined, max number of items defined', () => {
        const min = 0;
        const max = 5;

        const items = {
            key: "value"
        };
        const config = {
            [constants.ITEMS]: items,
            [constants.MAX_ITEMS]: max
        };
        const received = providerInstance.resolveArray(config);

        expect(received.length).inBetween(min, max);
        expect(providerInstance.itemResolution.mock.calls.length).inBetween(min, max);
    });

    test('items needed to be unique, and de-duplicated items are greater than min specified', () => {
        const min = 3;
        const max = 10;

        // Create at least two unique items, with third unique being offered
        providerInstance.itemResolution = jest.fn()
            .mockReturnValueOnce("a")
            .mockReturnValueOnce("b")
            .mockReturnValue("c");

        const items = {
            key: "value"
        };
        const config = {
            [constants.ITEMS]: items,
            [constants.MIN_ITEMS]: min,
            [constants.MAX_ITEMS]: max,
            [constants.UNIQUE_ITEMS]: true
        };
        const received = providerInstance.resolveArray(config);

        expect(received).toEqual(["a", "b", "c"]);
        expect(providerInstance.itemResolution.mock.calls.length).inBetween(min, max);
    });

    test('items needed to be unique, and created items are less than min specified', () => {
        const min = 3;
        const max = 5;

        // First few hits would return same items
        providerInstance.itemResolution = jest.fn()
            .mockReturnValueOnce("a")
            .mockReturnValueOnce("a")
            .mockReturnValueOnce("a")
            .mockReturnValueOnce("b")
            .mockReturnValueOnce("b")
            .mockReturnValue("c");

        const items = {
            key: "value"
        };
        const config = {
            [constants.ITEMS]: items,
            [constants.MIN_ITEMS]: min,
            [constants.MAX_ITEMS]: max,
            [constants.UNIQUE_ITEMS]: true
        };
        const received = providerInstance.resolveArray(config);

        expect(received).toEqual(["a", "b", "c"]);

        // Only with 6th call, we would get unique items > min
        expect(providerInstance.itemResolution).toBeCalledTimes(6);
    });
});


describe('resolveObject test cases', function () {

    let origItemResolution;

    beforeAll(() => {
        origItemResolution = providerInstance.itemResolution;
        providerInstance.itemResolution = jest.fn((config) => config.key);
    });

    afterEach(() => {
        providerInstance.itemResolution.mockClear();
    });

    afterAll(() => {
        providerInstance.itemResolution = origItemResolution;
    });


    test('type is array', () => {
        const origResolveArray = providerInstance.resolveArray;
        providerInstance.resolveArray = jest.fn(() => [1, 2]);

        const config = {
            [constants.TYPE]: constants.ARRAY
        };

        expect(providerInstance.resolveObject(config)).toEqual([1, 2]);
        expect(providerInstance.resolveArray).toBeCalledWith(config);
        providerInstance.resolveArray = origResolveArray;
    });

    test('object config is present at top level', function () {
        const config = {
            key_1: {
                key: "val_1"
            },
            key_2: {
                key: "val_2"
            },
            dummy: "str",
            key_3: {
                dummy: "xyz"
            },
            key_4: {
                key: false
            }
        };

        expect(providerInstance.resolveObject(config)).toEqual({key_1: "val_1", key_2: "val_2", key_4: false});
    });

    test('object has properties', function () {
        const config = {
            [constants.PROPERTIES]: {
                key_1: {
                    key: "val_1"
                },
                key_2: {
                    key: "val_2"
                },
                dummy: "str",
                key_3: {
                    dummy: "xyz"
                },
                key_4: {
                    key: false
                }
            },
            outer_key: {
                key: "not_included"
            },
            outer_str_key: "some_val"
        };

        expect(providerInstance.resolveObject(config)).toEqual({key_1: "val_1", key_2: "val_2", key_4: false});
    });

    test('object has additionalProperties with specified minimum properties', () => {
        const config = {
            [constants.ADDITIONAL_PROPERTIES]: {
                key: "add_prop_val",
                [constants.MIN_PROPERTIES]: 2
            },
            outer_key: {
                key: "not_included"
            },
            outer_str_key: "some_val"
        };

        expect(providerInstance.resolveObject(config)).toEqual(
            {artillery_load_test_0: "add_prop_val", artillery_load_test_1: "add_prop_val"}
        );
    });

    test('object has additionalProperties with no specified minimum properties', () => {
        const config = {
            [constants.ADDITIONAL_PROPERTIES]: {
                key: "add_prop_val",
            },
            outer_key: {
                key: "not_included"
            },
            outer_str_key: "some_val"
        };

        expect(providerInstance.resolveObject(config)).toEqual({});
    });

    test('object has additionalProperties which do not resolve', () => {
        const config = {
            [constants.ADDITIONAL_PROPERTIES]: {
                incorrect_key: "add_prop_val",
                [constants.MIN_PROPERTIES]: 2
            },
            outer_key: {
                key: "not_included"
            },
            outer_str_key: "some_val"
        };

        expect(providerInstance.resolveObject(config)).toEqual({});
    });

    test('object with both additional properties and properties', () => {
        const config = {
            [constants.PROPERTIES]: {
                key_1: {
                    key: "val_1"
                },
                key_2: {
                    key: "val_2"
                },
                dummy: "str",
                key_3: {
                    dummy: "xyz"
                },
                key_4: {
                    key: false
                }
            },
            [constants.ADDITIONAL_PROPERTIES]: {
                key: "add_prop_val",
                [constants.MIN_PROPERTIES]: 1
            },
            outer_key: {
                key: "not_included"
            },
            outer_str_key: "some_val"
        };

        expect(providerInstance.resolveObject(config)).toEqual(
            {key_1: "val_1", key_2: "val_2", key_4: false, artillery_load_test_0: "add_prop_val"}
        );
    });
});
