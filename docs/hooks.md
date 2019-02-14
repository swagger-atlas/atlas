Hooks
=====

(This is documentation for run time hooks for profiles are request.
If you are looking for Resource Mapping Hooks, visit [Resources](docs/resources.md) page)

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

```js
function filterByID(profiles) {
    return _.map(profiles, function (profile) { profile.id < 10; });
}
```

Things to note:
- It must take profiles and return profiles array
- Its hookRegister ID is "$profileSelection"


Profile Setup Hooks
-----
These are used to setup relevant data once the profile is selected.

Example:
```js
function addHeaders(profile) {
    profile.auth = {
        "headers": {'Authorization': 'Token ' + profile.token}
    };
    return profile;
}
```

Things to note:
- It must take single profile object and return it
- Its hookRegister ID is "$profileSetup"


Request Hooks
-----
These could be used to manipulate request parameters before sending request.
With this, for example, you can manipulate URL, request body etc

Example:
```js
function removeUserField(...args) {
    let body = args[1];
    del body.user;
    args[1] = body;
    return args;
}
```

Things to note:
- Each hook thus defined must take ...args and must return args.
- Number and order of arguments in return must not change
- For requests which support body (eg: POST/PUT/PATCH), args are in order: URL, BODY, REQUEST PARAMS
- For requests which do NOT support body (eg: GET), args are in order: URL, REQUEST PARAMS
- Relevant HookRegister ID is Swagger OPERATION ID for the request. This can be found in Swagger file of request


#### File Hooks

In the request hooks, we have a out-of-box solution for adding files to fields.

```js
file = require("./libs/files").file;

function addCSVFile(...args) {
    let body = args[1];
    body.upload_file = file.getCSVFile();
    args[1] = body;
    return args;
}
```

You can use following File Methods:
- getImageFile()
- getCSVFile()
- getExcelFile()
- getTextFile()
- getFileByPath(path) (In this, supply your own file by providing path)

**CAVEAT** : Make sure that the file fields is marked as type `file` in Swagger.
If not, it may result in unexpected behaviour.
When ATLAS finds `file` type fields, it automatically generates dummy text file for same


Hook Registration
-----

Once you define functions, you must register them via HookRegister.

For example, for above examples,

```js
exports.hookRegister = [
    ["$profileSelection", filterByID],
    ["$profileSetup", addHeaders],
    ["my_swagger_operation", removeUserField]
];
```

You can associate multiple hooks to a single operation.
In the case, hooks would be run in the order as they are defined in hookRegister.


Hook Chaining
-------------

This illustrates how a single operation can have multiple hooks associated with it


```js
function filterByID(profiles) {
    return _.filter(profiles, function (profile) { profile.id < 10; });
}

function selectiveWeight(profiles) {
    // Profile with frequency "heavy" to be weighed twice as much as others.
    let newProfiles = profiles;
    _.forEach(profiles, function(profile) {
        if (profile.frequency === "heavy") {
            newProfiles.push(profile);
        }
    };
    return newProfiles;
}

// In this case, first profiles would be filtered and then weighed
exports.hookRegister = [
    ["$profileSelection", filterByID],
    ["$profileSelection", selectiveWeight]
];
```
