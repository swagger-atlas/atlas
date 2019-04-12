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


Add InfluxDB and Grafana
------------------------

- Run `docker-compose -f docker/docker-compose.yml up`


With Artillery
--------------

(Make sure you have ATLAS installed in your virtualenv)
(Also, make sure you are running InfluxDB and Grafana)

- `npm install`
- `atlas dist`
- `atlas run`


Customization covered in this example
=====================================

- See `conf/profiles.yaml` for example of Multiple Profiles
- See `conf/hooks.py` and conf/resource_mapping.yaml` for example of Resource Hooks
