Integration Use Cases
=====================

This guide will explain some of the common use cases which are encountered while integrating the ATLAS with your project.
Some of these use cases are hinted while integrating your project.

Please also see these guides:
- [Profiles](profiles.md)
- [Resources](resources.md)


Authenticating APIs
-------------------

It is possible to provide Authentication to APIs.

- Editing `conf/profiles.yaml` and adding authentication key value pairs
- In `conf/artillery//hooks.js` change `setHeader()` function as needed.

*Example*
```yaml
# profiles.yaml
<profile_name>:
    token: abcd
```

```js
// hooks.js
function addHeaders(profile) {
    profile.auth = {
        "headers": {'Authorization': 'Token ' + profile.token}
    };
    return profile;
}
```

This header will now be added to all API Requests. We only support Header authentication for now


Hitting Selective APIs
----------------------

There are two ways to select which APIs to hit:

#### Tagging the APIs

You can specify tags in Swagger, and then mark them in Profiles.
This selects only those APIs which follow the tag schema.

This allows you to control the APIs at profile level

Profiles example:
```yaml
<profile_name>:
    <other_details>
    tags:
        tag_1
        tag_2
```

Also, mark `ONLY_TAG_API` as True in settings file.

#### Excluding the APIs

You can mark specific URLs to be not hit. This is a list of regex
This is global level setting, and affects all of your profiles

This is available in `EXCLUDE_URLS` Settings


Getting `Resource Pool Not Found/ Provider Check Failed` Error
--------------------------------------------------------------

Resources are dynamic entities which are marked and used by ATLAS.
To know more about them, please see [Resources](resources.md)

There are multiple ways in which these are created:

#### No APIs which produce Resources

There are no APIs which returns the resources we want.
This could be fixed by mapping the resource in `resource_mapping.yaml`

#### API returning resources is empty

Sometimes, the API which returns the response are empty.
This is sometimes due to ATLAS integration, and other times due to Server issues.
The easiest way is to fix is to map the resource in `resource_mapping.yaml`

#### API returning resources throws error

API responsible for returning resource is producing error.

There are multiple ways this could happen
- Swagger does not reflect the Server Request Body. Solution: Update Swagger
- Swagger does not capture the validations required by server.
Solution: Use `conf/artillery/hooks.py` file to update the request body to update the Request body
