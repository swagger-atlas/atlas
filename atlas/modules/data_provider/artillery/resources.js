_ = require('lodash');
settings = require('./settings');

const singleton = Symbol();
const singletonEnforcer = Symbol();


exports.Resource = class Resource {
    // Resource class is singleton
    // You have to use resource.instance to get resource, and not new Resource()

    constructor(enforcer) {
        if(enforcer !== singletonEnforcer) {
            throw "Cannot construct Singleton";
        }

        this.resources = {};

        // These resources are dynamically generated during build time.
        // Do not edit unless you know what you are doing
        let dynamicResources;
    }

    static get instance() {
        if(!this[singleton]) {
            this[singleton] = new Resource(singletonEnforcer);
        }
        return this[singleton];
    }

    static getKey(profile, resourceKey) {
        return profile + ":" + resourceKey;
    }

    getResource(profile, resourceKey, options = {}) {

        let values = this.resources[Resource.getKey(profile, resourceKey)];
        if (_.isEmpty(values)) {
            return new Set([]);
        }

        values = [...values];

        if (options.delete || options.items === 1) {
            let value = _.sample(values);

            if (!_.isNil(value) && options.delete) {
                this.deleteResource(profile, resourceKey, value);
            }

            values = _.isNil(value)  || value === "" ? [] : [value];
        }

        return new Set(_.isEmpty(values) ? []: values);
    }

    doesExist(profile, resourceKey, searchValue) {
        let values = this.resources[Resource.getKey(profile, resourceKey)];
        return _.isEmpty(values) ? false: values.has(searchValue);
    }

    updateResource(profile, resourceKey, resourceValues) {
        if (!_.isEmpty(resourceValues)) {
            const key = Resource.getKey(profile, resourceKey);

            if (this.resources[key]) {
                this.resources[key] = new Set([...resourceValues, ...this.resources[key]]);
            } else {
                this.resources[key] = new Set(resourceValues);
            }
        }
    }

    deleteResource(profile, resourceKey, resourceValue) {
        this.resources[Resource.getKey(profile, resourceKey)].delete(resourceValue);
    }

    restoreResource(profile, resourceKey, resourceValue) {
        this.resources[Resource.getKey(profile, resourceKey)].add(resourceValue);
    }
};
