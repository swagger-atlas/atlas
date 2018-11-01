_ = require('lodash');
Profiles = require('./profiles').profiles;

const singleton = Symbol();
const singletonEnforcer = Symbol();

class ProfileInstance {

    constructor(profileName) {
        this.profile = Profiles[profileName];
        this.profileName = profileName;
        this.headers = {};

        // Any Custom Setup functions
        this.customFuncQueue = [];
    }

    register(funcName) {
        this.customFuncQueue.push(funcName);
    }

    setUp() {
        for (let func of this.customFuncQueue) {
            func();
        }
    }
}


exports.Profile = class Profile {

    // Create a profileInstance available for all profiles available
    constructor(enforcer) {
        if(enforcer !== singletonEnforcer) {{
            throw "Cannot construct Singleton";
        }}

        const self = this;
        self.profiles = {};

        _.forEach(Profiles, function(value, key) {
            self.profiles[key] = new ProfileInstance(key);
        })
    }

    static instance(profileName) {
        if(!this[singleton]) {
            this[singleton] = new Profile(singletonEnforcer);
        }
        return this[singleton].profiles[profileName];
    }
};
