async function addHeaders(profile) {
    profile.auth = {
        "headers": {'Authorization': 'Token ' + profile.token}
    };
    return profile;
}

exports.hookRegister = [
    ["$profileSetup", addHeaders]
];


/*
Hooks basically let you inject custom code at various places during Load Testing.

Three types of Hooks are:
1. Profile Selection Hooks
2. Profile Setup Hooks
3. Request Body Hooks

After defining hooks, you should export them via `hookRegister`

Profile Selection Hooks
----
They are functions which you can write to filter out which profiles you want to select.
Currently, the convention is to randomly pick one profile from list of all profiles

Example of this type of hook:

function filterByID(profiles) {
    return _.filter(profiles, function (profile) { profile.id < 10; });
}

Things to note:
    - It must take profiles and return profiles array
    - Its hookRegister ID is "$profileSelection"


Profile Setup Hooks
-----
These are used to setup relevant data once the profile is selected.

Example:
async function addHeaders(profile) {
    profile.auth = {
        "headers": {'Authorization': 'Token ' + profile.token}
    };
    return profile;
}

Things to note:
    - It must take single profile object and returns profile (as part of promise contract)
    - Its hookRegister ID is "$profileSetup"


Request Hooks
-----
These could be used to manipulate request parameters before sending request.
With this, for example, you can manipulate URL, request body etc

Example:
function removeUserField(...args) {
    let body = args[1];
    del body.user;
    args[1] = body;
    return ...args;
}

Things to note:
    - Each hook thus defined must take ...args and must return args.
    - Number and order of arguments in return must not change
    - For requests which support body (eg: POST/PUT/PATCH), args are in order: URL, BODY, REQUEST PARAMS
    - For requests which do NOT support body (eg: GET), args are in order: URL, REQUEST PARAMS
    - Relevant HookRegister ID is Swagger OP_KEY for the request. (Swagger OP_KEY is "METHOD url")


Hook Registration
-----

Once you define functions, you must register them via HookRegister.

For example, for above examples,

exports.hookRegister = [
    ["$profileSelection", filterByID],
    ["$profileSetup", addHeaders],
    ["PUT /my/api/{id}", removeUserField]
];

You can associate multiple hooks to a single operation.
In the case, hooks would be run in the order as they are defined in hookRegister.

 */
