What is Artillery
=======

Artillery is a modern, powerful & easy-to-use load testing and functional testing toolkit.
Use it to ship scalable applications that stay performant & resilient under high load.
Artillery is documented at their [official site](https://artillery.io/docs/)


Short note on Artillery Commands
======
- In this documentation, artillery commands are given which are each relevant to their section.
- When you run `python manage.py dist artillery`, all these commands are run by default.
- In the dist command, you can toggle the features as needed


Artillery Setup for ATLAS
=====
When integrating ATLAS project with artillery, you would need to run one-time script which would install all required dependencies.
For artillery, setup is responsible for:

- Convert all required constants into a JS file and expose them
- Convert all required settings into a JS file and expose them

This step should be only executed if you change any settings value or update your ATLAS project.

`python manage.py setup artillery`


Basic Artillery Configuration
========

At the very least, we require two artillery Configuration to be filled by users:
- You need to enter your Swagger definition at `conf/swagger.yaml` location
- You need to enter your Profiles definition at `conf/profiles.yaml` [Profiles](profiles.md)

There are other possible configuration values, which are explained below in their respective sections


Resources in ATLAS
===
ATLAS relies heavily on something we term as "resources".
Generally speaking resources are entities for which we cannot fake data in ATLAS by normal means.
These could be for example, primary key values of your objects, tokens or specific values which cannot be captured via Swagger.

ATLAS has limited in-built intelligence where it tries to extract the resources and try to somehow get the values for them without human intervention.
This is not fool-proof however, and developer of the project might need to interject the values as required in some places.
See: [Resources](resources.md) for in-depth discussion of the same


Authenticating the APIs
======
If your APIs need authentication, you can leverage the `conf/artillery/hooks.js` for same.
- Your default file would have a function called `setHeaders` which assume you have added a token value in profiles.yaml file, and authenticates to Token Authentication
- However, you can change this function definition to enable or disable any kind of auth mechanism
- You can add or remove other hooks also and register them with `profile.register(<your_func_name>)` which would be run for each of your test user once.


Building Artillery Configuration for ATLAS
========
Once you have setup artillery, you want ATLAS to build the Swagger into artillery readable format.
This generally occurs in following steps:
- Identification of resources. Run `python manage.py detect_resources` for same. Unless, you are updating Swagger, this should be only run once.
- Run `python manage.py fetch_data` so we can extract all relevant values. One time operation unless you want to re-fetch all values again
- Run `python manage.py build artillery` which transforms your YAML Swagger to artillery YAML File (with lots of other awesome stuff besides)


Distributing Your Setup
=========

Finally, there is a magic command `python manage.py dist artillery`.
This will create a folder `dist`.

This is self-sufficient folder.
You can copy this folder and run it ANYWHERE where artillery is pre-installed. It does not NEED any other configurations or even access to your swagger schema


FAQ
=====

1. ATLAS is not creating proper data body for my APIs, which results in 400 failure. What are alternatives?
You can change any request body created by ATLAS prior to its hit. See `conf/artillery/hooks.js` for more details. Your operation ID is defined in Swagger.
