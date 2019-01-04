_ = require('lodash');


class RelationshipResources {

    constructor() {
        this.hashMap = {};
    }

    insert(resourceValueMap) {

        const self = this;

        const subSets = RelationshipResources.getSubsets(Object.keys(resourceValueMap));
        _.forEach(subSets, function (childSetKeys) {
            if (len(childSetKeys) > 1) {
                let childSet = _.pick(resourceValueMap, childSetKeys);
                self.hashMap[Object.keys(childSet).sort()] = childSet;
            }
        })
    }

    query(resources) {
        return _.get(this.hashMap, Object.keys(resources).sort())
    }

    static getSubsets(parentArray) {
        parentArray.reduce(
            (subsets, value) => subsets.concat(
                subsets.map(set => [value,...set])
            ),
            [[]]
        );
    }
}

exports.relationshipResource = RelationshipResources();
