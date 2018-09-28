import { K6Hook } from "./hookSetup.js";    // This will be corrected at dist. time, so no need to change it
import { Profile } from "./profile.js";

// Do NOT change name of identifiers
export let profile = new Profile("default");      // YOUR PROFILE NAME Goes here
export const hook = new K6Hook();

function setHeaders() {
    // You can change this as needed
    profile.headers = {'Authorization': 'Token ' + profile.profile.token};
}

profile.register(setHeaders);

/*
Define your functions and register them in hooks here.
For example:
function testHook(...args) {
    console.log("I am a test hook");
    return args;
}

hook.register("operationId", testHook);

Each hook thus defined must take ...args and must return args.
Number and order of arguments in return must not change

You can also define functions and register which you want to execute at start of testing cycle for each user
These are much simpler and are registered as:
`profile.register(funcName)` where funcName is your function
 */
