Profiles
=====

You may need profiles for:
- Storing authentication information specific to the profile
- May want to specify which APIs should be run for this type of users (eg. Student should not be running APIs accessible only to Staff)
- Easier way to ensure that resources which are fetched are specific to the profile


Creating and using Profiles
=======
In your conf folder, there would be `profiles.yaml`, in which you can create profiles.
ATLAS gives you a dummy profile, which you can over-write as needed.


Atlas Needs at least one profile, so even if you do not plan on using profiles, do NOT delete dummy profile.
You can define multiple profiles in ATLAS as needed.


After the creation of profiles, you can specify which profile to use in `hooks.js`
Using `profile.register` function, you can also specify any number of hooks which you want to run for profile before start of load test


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

And then in `conf/hooks.js`
```js
function setHeader() {
    profile.headers = {'Authorization': 'Token ' + profile.profile.token};
}
```

This header will now be added to all API Requests.


Using profiles for Resource Mapping Variables
=============================================

Please see [resources](resources.md) documentation for understanding of resources.

Profiles can store key value pairs which `resource_mapping` file can directly access.

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

Here `id` would be transplanted by value of 5.
