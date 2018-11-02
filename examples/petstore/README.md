Pet-store Example
=================

This is an application build on ATLAS framework


Running Server
==============

Go to server/ folder
Run `npm start`

This is based on NodeJS implementation (slightly modified) of [Swagger Codegen](https://github.com/swagger-api/swagger-codegen)


Running Load Test
=================

With Artillery
--------------

(Make sure you have ATLAS installed in your virtualenv)

- Run `python manage.py dist artillery`
- `artillery run dist/artillery.yaml`


Customization covered in this example
=====================================

- See `conf/profiles.yaml` for example of Multiple Profiles
- See `conf/resource_hooks.py` and conf/resource_mapping.yaml` for example of Resource Hooks
