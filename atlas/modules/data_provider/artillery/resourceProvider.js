_ = require('lodash');

const exceptions = require('./exceptions');

const EmptyResourceError = exceptions.EmptyResourceError;


exports.ResourceProvider = class ResourceProvider {
    constructor(resourceName, dbResourceProviderInstance) {
        this.resourceName = resourceName;
        this.dbResourceProviderInstance = dbResourceProviderInstance;
    }

    /*
    Options Available are:
        - delete: Whether to delete this resource while fetching. Default: false
        - items: Number of items to fetch. default: 1. Is always 1 for delete: true
    */
    static getOptions(options) {

        if(_.isNil(options)) {
            options = {};
        }

        if (_.isNil(options.items)) {
            options.items = 1;
        }

        if (_.isNil(options.delete)) {
            options.delete = false;
        }

        if (options.delete) {
            options.items = 1;
        }

        if (_.isNil(options.flatForSingle)) {
            options.flatForSingle = options.items === 1;
        }

        return options;
    }

    getResources(profile, options) {

        options = ResourceProvider.getOptions(options);

        // Several Lodash arguments work only on arrays, so converting here if set
        let resources = [...this.dbResourceProviderInstance.getResource(profile, this.resourceName, options)];

        if (_.isEmpty(resources)) {
            throw new EmptyResourceError(`Resource Pool not found for ${this.resourceName}`);
        }

        return options.flatForSingle ? resources[0] : resources;
    }

    restoreResource(profile, resourceValue) {
        // Function to restore Resource value in DB if delete Operation was un-successful
        this.dbResourceProviderInstance.restoreResource(profile, this.resourceName, resourceValue);
    }
};
