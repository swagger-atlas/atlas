const relationshipResource = require('../atlas/modules/data_provider/artillery/relationResources').relationshipResource;


describe('test query', function () {

    test('test with no resource values', () => {
        relationshipResource.hashMap = {
            "profile:a,b": new Set()
        };
        expect(relationshipResource.query(["a", "b"], "profile")).toEqual([])
    });

    test('test with resource values', () => {
        relationshipResource.hashMap = {
            "profile:a,b": new Set([
                '[1, 2]', '[1, 3]'
            ])
        };
        expect(relationshipResource.query(["a", "b"], "profile")).toEqual(
            [{"a": 1, "b": 2}, {"a": 1, "b": 3}]
        );
    });
});


describe('test insertion', function () {

    test('no resource value map provided', () => {
        relationshipResource.hashMap = {};
        relationshipResource.insert({}, "profile");
        expect(relationshipResource.hashMap).toEqual({});
    });

    test('insertion of keys', () => {
        relationshipResource.hashMap = {
            "profile:a,b": new Set(['[1,3]'])
        };

        let resMap = {
            "a": new Set([1]),
            "b": new Set([2]),
            "c": 3
        };

        relationshipResource.insert(resMap, "profile");

        expect(relationshipResource.hashMap).toEqual({
            "profile:a,b": new Set(['[1,2]', '[1,3]']),
            "profile:a,c": new Set(['[1,3]']),
            "profile:b,c": new Set(['[2,3]']),
            "profile:a,b,c": new Set(['[1,2,3]']),
        });

    });

    test('cross-product relations does not insert themselves', () => {
        relationshipResource.hashMap = {
            "profile:a,b": new Set(['[1,3]'])
        };

        let resMap = {
            "a": new Set([1, 5]),
            "b": [2, 4],
            "c": new Set([3])
        };

        relationshipResource.insert(resMap, "profile");

        expect(relationshipResource.hashMap).toEqual({
            "profile:a,b": new Set(['[1,3]']),
            "profile:a,c": new Set(['[1,3]', '[5,3]']),
            "profile:b,c": new Set(['[2,3]', '[4,3]'])
        });
    });
});
