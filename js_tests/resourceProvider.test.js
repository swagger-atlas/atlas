const ResourceProvider = require('../atlas/modules/data_provider/artillery/resourceProvider').ResourceProvider;
const Resource = require('../atlas/modules/data_provider/artillery/resources').Resource;
const exceptions = require('../atlas/modules/data_provider/artillery/exceptions');

resourceInstance = Resource.instance;
resourceProviderInstance = new ResourceProvider("resource", resourceInstance);
const EmptyResourcesError = exceptions.EmptyResourceError;


describe('resource provider test cases', () => {

    test("restoreResource calls resource instance restore", () => {
        resourceInstance.restoreResource = jest.fn();

        resourceProviderInstance.restoreResource("profile", [1, 2]);

        expect(resourceInstance.restoreResource).toHaveBeenCalledWith("profile", "resource", [1, 2]);
        resourceInstance.restoreResource.mockClear();
    });

    describe('getResource test cases', () => {

        test('empty resources throw error', () => {
            resourceInstance.getResource = jest.fn(() => []);

            expect(() => {
                resourceProviderInstance.getResources("profile");
            }).toThrow(EmptyResourcesError);
        });

        test('options with item one returns single', () => {
            resourceInstance.getResource = jest.fn(() => [1, 2, 3]);
            expect(resourceProviderInstance.getResources("profile", {items: 1})).toBe(1);
        });

        test('getResources return array', () => {
            resourceInstance.getResource = jest.fn(() => [1, 2, 3]);
            expect(resourceProviderInstance.getResources("profile", {items: "multiple"})).toEqual([1, 2, 3]);
        });
    });

    describe('getOptions test cases', () => {

        test('empty options returns default options', () => {
            expect(ResourceProvider.getOptions({})).toEqual({
                items: 1,
                flatForSingle: true,
                "delete": false
            })
        });

        test('options with no items mark items as 1', () => {
            expect(ResourceProvider.getOptions({key: "value"})).toEqual({
                items: 1,
                flatForSingle: true,
                "delete": false,
                key: "value"
            })
        });

        test('options with items affect flatForSingle', () => {
            expect(ResourceProvider.getOptions({items: 2})).toEqual({
                items: 2,
                flatForSingle: false,
                "delete": false
            })
        });

        test('options with delete true mark items as one', () => {
            expect(ResourceProvider.getOptions({items: 2, "delete": true})).toEqual({
                items: 1,
                flatForSingle: true,
                "delete": true
            })
        });

        test('options with explicit flat For Single', () => {
            expect(ResourceProvider.getOptions({flatForSingle: false})).toEqual({
                items: 1,
                flatForSingle: false,
                "delete": false
            })
        });
    });

});
