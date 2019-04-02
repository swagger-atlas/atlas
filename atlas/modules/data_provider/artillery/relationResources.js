_ = require('lodash');


/*
    Takes two arrays and return their cartesian product:

    Example:
        cartesianHelper([1, 2], [3, 4]) would give output:
        [
            [1, 3], [1, 4], [2, 3], [2, 4]
        ]
 */
cartesianHelper = (a, b) => {
    return [].concat(...a.map(d => b.map(e => [].concat(d, e))));
};


/*
    Takes any number of arrays and return their cartesian product.
    Example:
        cartesianHelper([1, 2], [3, 4], [5, 6]) would give output:
        [
            [1, 3, 5], [1, 3, 6], [1, 4, 5], [1, 4, 6], [2, 3, 5], [2, 3, 6], [2, 4, 5], [2, 4, 6]
        ]
    Recursively calls itself by resolving first two arrays using cartesianHelper
 */
cartesian = (a, b, ...c)  => {
    return b ? cartesian(cartesianHelper(a, b), ...c) : a;
};


/*
    Please see `reference/resource-relationships` for more information
 */
class RelationshipResources {

    constructor() {
        this.hashMap = {};
    }

    static getKey(profile, resourceKeys) {
        return profile + ":" + resourceKeys.sort();
    }

    insert(resourceValueMap, profile) {

        const self = this;
        const subSets = RelationshipResources.getSubsets(Object.keys(resourceValueMap));

        _.forEach(subSets, function (childSetKeys) {
            if (childSetKeys.length > 1) {
                let childSet = _.pick(resourceValueMap, childSetKeys);
                let childValues = RelationshipResources.getValues(childSet);
                const key = RelationshipResources.getKey(profile, Object.keys(childSet));

                if (!childValues) {
                    console.warn(`Multiple Values for Multiple resources for ${key}. Skipping the insertion of related resources`);
                    return;
                }

                if (_.isUndefined(self.hashMap[key])) {
                    self.hashMap[key] = new Set();
                }

                _.forEach(childValues, function(value) {
                    // JS Sets work with references, so would keep adding same Array multiple times
                    self.hashMap[key].add(JSON.stringify(value));
                });
            }
        });
    }

    static getValues(mapping) {
        const keys = Object.keys(mapping).sort();

        let values = [];

        _.forEach(keys, function (key) {
            let elValue = mapping[key];
            elValue = (_.isArray(elValue) || elValue instanceof Set) ? [...elValue] : [elValue];
            values.push(elValue);
        });

        // We do not want to deal with multiple resources having multiple values
        if (_.filter(values, arr => arr.length > 1).length > 1) {
            return false;
        }

        // We need to get cartesian product for insertion
        // For example, if Resource A is [1], and Resource B is [2, 3], then valid values are [[1, 2], [1, 3]]
        return cartesian(...values);
    }

    static getSubsets(parentArray) {
        return parentArray.reduce(
            (subsets, value) => subsets.concat(
                subsets.map(set => [value,...set])
            ),
            [[]]
        );
    }

    query(resources, profile) {
        let resourceValues = this.hashMap[RelationshipResources.getKey(profile, resources)];
        const keys = resources.sort();
        let returnValue = [];

        if (!_.isEmpty(resourceValues)) {
            _.forEach([...resourceValues], val => {
                returnValue.push(_.zipObject(keys, JSON.parse(val)))
            });
        }

        return returnValue;
    }
}

exports.relationshipResource = new RelationshipResources();
