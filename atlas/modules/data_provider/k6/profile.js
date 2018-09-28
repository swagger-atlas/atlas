import { profiles as Profiles } from './profiles.js'


export class Profile {
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