_ = require("lodash");

constants = require('./constants');
settings = require('./settings');
Resource = require('./resources').Resource;
relatedResources = require("./relationResources").relationshipResource;
const FakeData = require("./fakeProvider").FakeData;
const ResourceProvider = require("./resourceProvider").ResourceProvider;
const exceptions = require("./exceptions");

const InvalidDataOptionsError = exceptions.InvalidDataOptionsError;


class Provider {
    /*
        This class is responsible for generating data for given schema.
        Data generation may be done from DB cache or from fake methods
     */

    constructor(profile=null) {
        this.profile = profile;
        this.dbResourceProviderInstance = Resource.instance;

        this.configResourceMap = {};
        this.relatedResourceData = {};
    }

    rollBackDelete(resource, value) {
        const resourceProvider = new ResourceProvider(resource, this.dbResourceProviderInstance);
        resourceProvider.restoreResource(this.profile, value);
    }

    reset() {
        this.configResourceMap = {};
        this.relatedResourceData = {};
    }

    static getFakeData(config) {
        const fakeFunc = FakeData.getFakeMapper(config);

        let ret = null;

        if (fakeFunc) {
            ret = fakeFunc(config);
        }

        return ret;
    }

    getResource(resource, options) {
        const resourceProvider = new ResourceProvider(resource, this.dbResourceProviderInstance);
        const independentResourceValue = resourceProvider.getResources(this.profile, options);
        let resourceValue = this.relatedResourceData[resource];

        if (_.isUndefined(resourceValue)) {
            resourceValue = independentResourceValue;
        }

        this.configResourceMap[resource] = new Set(_.isArray(resourceValue) ? resourceValue: [resourceValue]);
        return resourceValue;
    }

    itemResolution(config) {
        const resource = _.get(config, constants.RESOURCE);
        let retValue;

        if (resource) {
            retValue = this.getResource(resource, config.options);
        } else {
            let itemType = _.get(config, constants.TYPE);

            if (!itemType) {
                throw new InvalidDataOptionsError(`Item type must be defined - ${JSON.stringify(config)}`);
            }

            if (itemType === constants.ARRAY) {
                retValue = this.resolveArray(config);
            } else if (itemType === constants.OBJECT) {
                retValue = this.resolveObject(config);
            } else {
                retValue = Provider.getFakeData(config);
            }
        }

        return retValue;
    }

    getRelatedResources(resources) {

        const self = this;

        if (!_.isEmpty(resources)) {
            let resourceValueMap = relatedResources.query(resources, this.profile);

            let validMap = _.filter(resourceValueMap, singleMap => {
                return _.every(singleMap, (value, key) => {
                    return self.dbResourceProviderInstance.doesExist(self.profile, key, value);
                });
            });

            self.relatedResourceData =  _.sample(validMap) || {};
        }
    }

    resolveArray(config) {
        const itemConfig = _.get(config, constants.ITEMS);
        const self = this;

        if (_.isEmpty(itemConfig)) {
            throw new InvalidDataOptionsError(`Items should be defined for Array type - ${JSON.stringify(itemConfig)}`)
        }

        const minItems = _.get(config, constants.MIN_ITEMS, 0);
        const maxItems = _.get(config, constants.MAX_ITEMS, Math.max(10, minItems + 1));

        let items = _.range(_.random(minItems, maxItems)).map(() => self.itemResolution(itemConfig));

        if (_.get(config, constants.UNIQUE_ITEMS, false)) {
            items = new Set(items);
            // If due to de-duplication, our array count decreases and is less than what is required
            while (items.size < minItems){
                items.add(self.itemResolution(itemConfig));
            }
            items = Array.from(items);
        }
        return items;
    }

    resolveObject(config) {

        // Short-circuit return if Type is Array
        let itemType = _.get(config, constants.TYPE);
        if (itemType === constants.ARRAY) {
            return this.resolveArray(config);
        }

        // We want to respect empty properties and additional properties
        let properties = config[constants.PROPERTIES];
        let additionalProperties = config[constants.ADDITIONAL_PROPERTIES];
        const self = this;

        if(!properties && !additionalProperties) {
            // This may be manual, so try treating whole object as properties
            properties = {};
            _.forEach(config, function(value, key) {
                if (typeof value === "object") {
                    properties[key] = value;
                }
            })
        }

        if (!properties) {
            properties = {};
        }

        if (!additionalProperties) {
            additionalProperties = {};
        }

        let dataObject = {};

        _.forEach(properties, function(propConfig, name) {
            const itemValue = self.itemResolution(propConfig);
            if (!_.isNil(itemValue)) {
                dataObject[name] = itemValue;
            }
        });

        if (!_.isEmpty(additionalProperties)) {
            const addPropMapper = self.itemResolution(additionalProperties);
            if (addPropMapper) {
                // Generate minimum possible additional properties
                _.forEach(_.range(_.get(additionalProperties, constants.MIN_PROPERTIES, 0)), function (index) {
                    dataObject["artillery_load_test_" + index] = addPropMapper;
                });
            }
        }

        return dataObject;
    }
}


class ResponseDataParser {
    /*
        This class is responsible for parsing responses and updating cached DB as per response
     */

    constructor(profile=null) {
        this.profile = profile;
        this.dbResourceInstance = Resource.instance;
    }

    parseArray(schema, response) {

        const self = this;
        let reqArr = [];

        if (_.isEmpty(response)) {
            return reqArr;     // Short-circuit return
        }

        const itemConfig = _.get(schema, constants.ITEMS, {});

        if (typeof response[0] === "object") {

            // Run the Parser for first 10 values, which should be sufficient
            _.forEach(_.slice(response, 0, 10), function (value) {
                reqArr.push(
                  self.parser(_.get(itemConfig, constants.PROPERTIES, itemConfig), value)
                );
            });
        } else {
            let resource = _.get(itemConfig, constants.RESOURCE);

            if (!_.isNil(resource)) {
                const newResources =  self.addData(resource, response);
                if (!_.isEmpty(newResources)) {
                  reqArr = {[resource]: newResources};
                }
            }
        }

        return reqArr;
    }

    parseObject(schema, response) {
        /*
        Need to return an object which could be fed to formatResourceMap.
        We need to make sure that we handle arbitrary nesting level of response and schema
        Further, we want to make that when we combine values of different resources, it makes for sensible relation

        Consider the somewhat contrived response
        (and assume that schema declares all of them as resources with correct type checks):

        {
            some_key: [
                {
                    x: 1
                },
                {
                    x: 2
                }
            ],
            y: 1,
            k: [3, 4],
            outer: {
                inner: [
                    {a: 1, b: 1},
                    {a: 1, b: 3}
                ],
                z: 2
            }
        }

        Then we would want our reqMap to look like:

        {
            y: new Set([1]),
            z: new Set([2]),
            $agg: [
                {
                    a: new Set([1]),
                    b: new Set([1])
                },
                {
                    a: new Set([1]),
                    b: new Set([3])
                },
                {x: new Set([1])},
                {x: new Set([2])},
                {k: new Set([3, 4])}
            ]
        }

        Notice that all simple keys where there is no confusion for cross-product are merged at top level
        All complicated aggregations are flattened as much as possible, and used.
         */

        let reqMap = {};

        const self = this;

        _.forEach(schema, function (schemaConfig, key) {

            if (_.isNil(response[key])) {
                return;     // Short-circuit return
            }

            if (_.isArray(response[key])) {
                // For sibling arrays in an object, cross-product do not make sense
                // So, for simplicity, add them as part of single array
                reqMap.$agg = _.concat(
                  reqMap.$agg || [], self.parseArray(schemaConfig, response[key])
                );
            } else if (typeof schemaConfig === "object" && schemaConfig.constructor === Object) {
                // First check if resource is available
                let resource = _.get(schemaConfig, constants.RESOURCE);
                if (!_.isNil(resource)) {
                    const newResources = self.addData(resource, response[key]);
                    if (!_.isEmpty(newResources)) {
                      reqMap[resource] = newResources;
                    }

                } else if (typeof response[key] === "object" && response[key].constructor === Object){
                    // Expect that if Response has objects, then schema would have object
                    // It is much faster than checking each properties in schema
                    const nestedObj = self.parser(_.get(schemaConfig, constants.PROPERTIES, schemaConfig), response[key]);
                    const newArr = _.concat(nestedObj.$agg || [], reqMap.$agg || []);
                    _.extend(reqMap, nestedObj);
                    reqMap.$agg = newArr;
                }
            }
        });

        return reqMap;
    }

    /*
        Entry Point for this class.
     */
    resolve(schema, response, reqResourceMap) {

        // Priority is given to resources in reqResourceMap
        const resourceMap = {...this.parser(schema, response), ...reqResourceMap};
        let self = this;

        if (!_.isEmpty(resourceMap)) {
            const outputResources = this.formatResourceMap(resourceMap);
            _.forEach(outputResources, (element) => {
                relatedResources.insert(element, self.profile);
            });
        }

        return true;
    }

    formatResourceMap(resourceMap) {
        /*
        Consider the resource map as:

        {
            $agg: [
                {x: 1},
                {x: 2},
                {
                    $agg: [
                        {a: 1, b: 1},
                        {a: 1, b: 3}
                    ]
                }
            ],
            y: 1,
            z: 1
        }

        We can not make assumptions how inner and outer aggregate resource result would be valid relationship

        Thus our final output should be:

        [
            {x: 1, y: 1, z: 1},
            {x: 2, y: 1, z: 1},
            {a: 1, b: 1, y: 1, z: 1},
            {a: 1, b: 3, y: 1, z: 1}
        ]

        To see how resourceMap is constructed and why we take assumptions stated above,
        see parseObject function (with parseArray and parser as its helpers)
         */

        let out = [];
        let element = _.isArray(resourceMap) ? {} : _.omit(resourceMap, '$agg');

        let self = this;

        _.forEach(resourceMap.$agg, (arrElement) => {
            const newElement = {...element, ...arrElement};
            if (arrElement.$agg) {
                // Array extend
                out.push(...self.formatResourceMap(newElement));
            } else {
                // Array Push
                out.push(newElement);
            }
        });

        return out;
    }

    parser(schema, response) {
        return _.isArray(response) ? this.parseArray(schema, response) : this.parseObject(schema, response);
    }

    addData(resourceKey, values) {
        const newResources = new Set(_.isArray(values) ? values: [values]);

        if (!_.isEmpty(newResources))
        {
            if(!settings.NOT_UPDATE_RUN_TIME_RESOURCES.has(resourceKey)) {
                this.dbResourceInstance.updateResource(this.profile, resourceKey, newResources);
            }
        }

        return newResources;
    }

    deleteData(resourceKey, resourceValue) {
        this.dbResourceInstance.deleteResource(this.profile, resourceKey, resourceValue);
        return true;
    }
}


module.exports = {
    Provider: Provider,
    ResponseDataParser: ResponseDataParser
};
