Profiles
========

Profiles are used in ATLAS to stimulate a role of an user who is running the application.
Within each profile, you can store user-specific details.
When running Load test, ATLAS will randomly distribute profiles among users for load testing.

You may need profiles for:
- Storing authentication information specific to the profile
- May want to specify which APIs should be run for this type of users (eg. Student should not be running APIs accessible only to Staff)
- A way to ensure that resources could mapped to a specific profile


Creating and using Profiles
===========================

In your conf folder, there would be `profiles.yaml`, in which you can create profiles.
ATLAS gives you a dummy profile, which you can over-write as needed.

Atlas Needs at least one profile, so even if you do not plan on using profiles, do NOT delete dummy profile.
You can define multiple profiles in ATLAS as needed.

You can specify number of default actions which needed to be taken to setup any profile.
In `conf/artillery/hooks.js`, you can use `$profileSetup` as OP_KEY to run any number of hooks as needed.
One default hook is already available for users as template


Profile Distribution
====================

In case of multiple profiles, ATLAS default behaviour is to select a random profile for any simulated VU.
You can change this behaviour by adding a hook with OP_KEY `$profileSelection`.

The corresponding function takes all profiles as inputs and return the profile Array

An example snippet for same:

```js
function filterByID(profiles) {
    return _.filter(profiles, function (profile) { profile.id < 10; });
}
```


Using Profiles for Tagging
==========================

In the settings file, mark `ONLY_TAG_API` as True

In profiles.yaml, make these changes
```yaml
<profile_name>:
    <other_details>
    tags:
        tag_1
        tag_2
```

These tags correspond to your swagger file.
If any of these tags matches any of tags in Swagger, we hit that API, else we ignore it.


Using Profiles for Authentication
=================================

Profiles can store authentication key-value pairs.

*Example*
```yaml
<profile_name>:
    token: abcd
```

If it is a sensitive data which you do not want to commit, use `credentials.yaml`

```yaml
<profile_name>:
    username: ""
    password: ****
```


And then in `conf/artillery/hooks.js`
```js
async function addHeaders(profile) {
    profile.auth = {
        "headers": {'Authorization': 'Token ' + profile.token}
    };
    return profile;
}
```

Or a more complicated workflow sample which hits Server for actual Auth, and sets cookie

```js

function login(profile) {
    return new Promise((resolve, reject) => {
        request.post(
            loginURL, {             // Replace with actual URL
                body: JSON.stringify({
                    username: profile.username,
                    password: profile.password
                })
            }, function (err, httpResponse, body) {
                if (err) {
                    reject(err);
                }
                resolve(httpResponse);
            }
        );
    });
}


async function addHeaders(profile) {

    let authCookie = "";
    let respCookies = "";

    await login(profile)
        .then(
            (response) => {
                const body = JSON.parse(response.body);
                authCookie = body.Token;
                respCookies = response.headers['set-cookie'][0];
            }
        );

    profile.auth = {
        headers: {
            'Cookie': `user_auth_token=${authCookie}; ${respCookies}`
        }
    };

    return profile;
}
```

These headers will now be added to all API Requests.


Using profiles for Resource Mapping Variables
=============================================

Please see [resources](resources.md) documentation for understanding of resources.

Profiles can store key-value pairs which `resource_mapping` file can directly access.

*Example*
```yaml
<profile_name>:
    id: 5
```

And then in `resource_mapping` file
```
courses
    sql: select id from courses_courses c join student_courses s on c.id = s.course_id where s.student_id = {id}
```

Here `id` would be transplanted by the value of 5.


Linking Custom Scenario to Profiles
===================================

If you specify custom scenario, you need to link them to profiles.
Each profile by default executes `default` scenario which consists of all APIs.

You can change this mapping by keyword `scenarios`

*Example*
```yaml
<profile_name>:
    scenarios:
        - simple
<another_profile>:
    scenarios:
        - extended
```

And in `conf/conf.py`,
```py
from . import scenarios

LOAD_TEST_SCENARIOS = {
    "simple": scenarios.SIMPLE,
    "extended": scenarios.EXTENDED
}
```

*scenarios.py*
```py
from . import routes

SIMPLE = [
    routes.CREATE_XYZ,
    routes.LIST_XYZ,
    routes.UPDATE_XYZ
]

EXTENDED = [
    *SIMPLE,
    routes.RETRIEVE_XYZ,
    routes.CREATE_XYZ_ABC,
    routes.DELETE_XYZ_ABC,
    routes.DELETE_XYZ
]
```

where `routes.py` is generated via `atlas generate_routes`
