const Resource = require('../atlas/modules/data_provider/artillery/resources').Resource;


const resourceInstance = Resource.instance;


describe('resource test cases', () => {

    afterEach(() => {
            // Clear resources after each test cases to clear the bleed
            resourceInstance.resources = {};
        });

    test('constructor raises error', () => {
        expect(() => new Resource()).toThrow();
    });

    test('resource is a singleton', () => {
        expect(Resource.instance).toBe(resourceInstance);
    });

    test('getKey returns key combination of profile and resource', () => {
        expect(Resource.getKey("profile", "resource")).toBe("profile:resource");
    });

    describe('test getResource', () => {

        test('returns empty set if key does not exist', () => {
            expect(resourceInstance.getResource("profile", "resource")).toEqual(new Set());
        });

        test('returns empty set if key has empty values', () => {
            resourceInstance.resources = {
                [Resource.getKey("profile", "resource")]: new Set()
            };
            expect(resourceInstance.getResource("profile", "resource")).toEqual(new Set());
        });

        test('returns set of values if key has values', () => {
            resourceInstance.resources = {
                [Resource.getKey("profile", "resource")]: new Set([1, 2, 3])
            };
            expect(resourceInstance.getResource("profile", "resource")).toEqual(new Set([1, 2, 3]));
        });

        test('returns a single value if options has items as 1', () => {
            resourceInstance.resources = {
                [Resource.getKey("profile", "resource")]: new Set([1, 2, 3])
            };
            expect(resourceInstance.getResource(
                "profile", "resource", {items: 1}
            )).isSubSet(new Set([1, 2, 3]));
        });

        test('returns empty set if options has items as 1 and value is blank', () => {
            resourceInstance.resources = {
                [Resource.getKey("profile", "resource")]: new Set([""])
            };
            expect(resourceInstance.getResource(
                "profile", "resource", {items: 1}
            )).toEqual(new Set([]));
        });

        test('returns a single value and remove it from resources if delete is true', () => {
            resourceInstance.resources = {
                [Resource.getKey("profile", "resource")]: new Set([1, 2])
            };
            expect(resourceInstance.getResource(
                "profile", "resource", {"delete": true}
            )).isSubSet(new Set([1, 2]));

            expect(resourceInstance.resources[Resource.getKey("profile", "resource")].size).toBe(1);
        });

    });

    describe('test doesExist', () => {

        test('if value exist in resource, should return true', () => {
            resourceInstance.resources = {
                [Resource.getKey("profile", "resource")]: new Set([1, 2, 3])
            };
            expect(resourceInstance.doesExist("profile", "resource", 1)).toBe(true);
        });

        test('if value does not exist in resource, should return false', () => {
            resourceInstance.resources = {
                [Resource.getKey("profile", "resource")]: new Set([1, 2, 3])
            };
            expect(resourceInstance.doesExist("profile", "resource", 4)).toBe(false);
        });

        test('if resource does not exist, should return false', () => {
            expect(resourceInstance.doesExist("profile", "resource", 1)).toBe(false);
        });
    });

    describe('test updateResource', () => {

        test('does not update if it is empty', () => {
            resourceInstance.resources = {
                [Resource.getKey("profile", "resource")]: new Set([1, 2, 3])
            };

            resourceInstance.updateResource("profile", "resource", []);

            expect(resourceInstance.resources[Resource.getKey("profile", "resource")]).toEqual(new Set([1, 2, 3]));
        });

        test('create a new key in resources if does not exist', () => {
            resourceInstance.resources = {};

            resourceInstance.updateResource("profile", "resource", [2, 4, 6]);

            expect(resourceInstance.resources[Resource.getKey("profile", "resource")]).toEqual(new Set([2, 4, 6]));
        });

        test('updates values in resources if does exist', () => {
            resourceInstance.resources = {
                [Resource.getKey("profile", "resource")]: new Set([1, 2, 3])
            };

            resourceInstance.updateResource("profile", "resource", [2, 4, 6]);

            expect(resourceInstance.resources[Resource.getKey("profile", "resource")]).toEqual(
                new Set([1, 2, 3, 4, 6])
            );
        });
    });

    test('deleteResource deletes resource', () => {
        resourceInstance.resources = {
            [Resource.getKey("profile", "resource")]: new Set([1, 2, 3])
        };

        resourceInstance.deleteResource("profile", "resource", 2);

        expect(resourceInstance.resources[Resource.getKey("profile", "resource")]).toEqual(new Set([1, 3]));
    });

    test('restoreResource restores resource', () => {
        resourceInstance.resources = {
            [Resource.getKey("profile", "resource")]: new Set([1, 3])
        };

        resourceInstance.restoreResource("profile", "resource", 2);

        expect(resourceInstance.resources[Resource.getKey("profile", "resource")]).toEqual(new Set([1, 2, 3]));
    });

});
