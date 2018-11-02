_ = require("lodash");
ArtilleryHook = require("./hookSetup").ArtilleryHook;
profiles = require("./profiles").profiles;

// Do NOT change name of identifiers
const hook = new ArtilleryHook();

function selectProfile() {
    // You should change this logic if you do not want to select Profiles randomly
    const profileName = _.sample(Object.keys(profiles));
    let profile = profiles[profileName];

    // You can change the statements as needed
    profile.auth = {
        "headers": {'Authorization': 'Token ' + profile.token}
    };
    return {[profileName]: profile};
}

module.exports = {
    // profile: profile,
    hook: hook,
    selectProfile: selectProfile
};

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
