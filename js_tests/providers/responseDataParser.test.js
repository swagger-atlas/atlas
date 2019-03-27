const rewire = require('rewire');

const provider = rewire('../../atlas/modules/data_provider/artillery/providers');

const ResponseDataParser = provider.ResponseDataParser;
const respDataParser = new ResponseDataParser("profile");


describe('unit test resolve', () => {

    let relatedResources;

    beforeAll(() => {
        relatedResources = provider.__get__('relatedResources');
        relatedResources.insert = jest.fn();
    });

    beforeEach(() => {
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

