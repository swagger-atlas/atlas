Profiles
=====

Profiles are a way for ATLAS to distinguish between different types of users.
You may need profiles for:

- Authentication information specific to the profile
- May want to specify which APIs should be run for this type of users (eg. Student should not be running APIs meant to Staff)
- Easier way to ensure that resources which are fetched are specific to the profile


Creating and using Profiles
=======
In your conf folder, there would be `profiles.yaml`, in which you create profiles.
ATLAS gives you a dummy profile, which you can over-write as needed.


After the creation of profiles, you can specify which profile to use in `hooks.js`
Using `profile.register` function, you can also specify any number of hooks which you want to run for profile before start of load test
