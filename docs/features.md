Quick Feature Overview
======================

###### What ATLAS Does

- Converts Swagger to Load Test file seamlessly
- Generates fake Data for testing.
- Understands resource dependencies and workflow -
    eg: if one API creates PET, and another API wants to use Pet ID,
    ATLAS is intelligent enough to:
    - Order the APIs so that CREATE API comes before any API which wants to use the IDs
    - Transfer the resource dependency
    - This works with arbitrarily with any complex relationships between APIs as long it is not cyclic

Do Read [Best Practices](docs/best_practices.md) for swagger practices to get most out of ATLAS Automation systems.

###### Quick Run
- Copy Swagger in `conf/swagger.yaml`
- python manage.py dist artillery
- artillery dist/artillery.yaml


###### Authenticating APIs - Header Authentication
- Edit `conf/profiles.yaml` and add authentication information necessary
- In `conf/hooks.js` change `setHeader()` function as needed.


###### Load Test Configuration
- Edit `dist/artillery.yaml` file and change `duration` and `arrivalRate` as needed


###### Editing Specific API Request
- If you want to change the request to specific API, locate its OperationID in Swagger
- in `conf/hooks.js`, add a function which changes the request parameters, and hook it up with operationID


###### Fetching URL/Body Resources from DB
It is possible to generate real data from DB for some fields while load testing to reduce error rates
- First, connect your DB settings in `settings.py`
- Check `resource_mapping.yaml` and change the settings as necessary.

See **Mapping Resources to Database** section in [Resources](resources.md) for details

###### Custom Data
Instead of DB, you can also hook up custom data population.
- Edit `resource_mapping.yaml`
- Write your custom data function in `resource_hooks.py`

See **Mapping Resources to Database** section in [Resources](resources.md) for details


###### Selective API Hits
You may want to load test a subset of APIs only. There are several quick ways to do that
- Exclude URLs: In settings, you can give list of Regex for excluding URLs
- Tag Specific: (tags are same as those given in swagger)
    - In settings, mark ONLY_TAG_API as True
    - In `conf/profiles.yaml`, in tags section, mark the tags you want to test with

See [Profiles](profiles.md) for tagging example
