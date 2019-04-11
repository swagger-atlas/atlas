ATLAS
=====

ATLAS takes your Swagger, and smartly generates the code which could be used as input to various load testing tools.
Currently, ATLAS fully supports [Artillery Load Runner](https://artillery.io/)

ATLAS Stands for Automated Tool for Load Analysis and Simulation


Creating a new Project
======================
- Create a virtual environment. We only support Python 3.6+.
- Install the Atlas Project by `pip install swagger-atlas`
- Run `atlas newproject <project_name>`
- Switch to new directory
- Follow the README of directory to customize and run your load test


Features
========

#### What ATLAS Does

- Converts Swagger to Load Test file seamlessly
- Generates fake Data for testing.
- Understands resource dependencies and workflow -
    eg: if one API creates PET, and another API wants to use Pet ID,
    ATLAS is intelligent enough to:
    - Order the APIs so that CREATE API comes before any API which wants to use the IDs
    - Transfer the resource dependency
    - This works with arbitrarily with any complex relationships between APIs as long it is not cyclic
- Generate beautiful graphics and statistics

Do Read [Use Cases](docs/use_cases.md) for use cases and best swagger practices to get the most out of ATLAS Automation systems.

---

#### Authenticating APIs
It may be possible that you need to provide Authentication Information with APIs.
With ATLAS, you can provide Header Authentication by:

- Editing `conf/profiles.yaml` and adding authentication key value pairs
- In `conf/artillery/hooks.js` change `addHeaders()` function as needed.

*Example*
```yaml
# profiles.yaml
<profile_name>:
    token: abcd
```

```js
// hooks.js
async function addHeaders(profile) {
    profile.auth = {
        "headers": {'Authorization': 'Token ' + profile.token}
    };
    return profile;
}
```

This header will now be added to all API Requests. We only support Header authentication for now


#### Load Test Configuration
You should be able to edit load test configuration by following respective runner.
For Artillery see [CLI Options](https://artillery.io/docs/cli-reference/)


Configuring ATLAS
=================

ATLAS is highly automated system, however you may want to configure it to suit your needs.
A quick overview of most frequent configuration options:

#### Manual Data Generation
ATLAS has an inbuilt AI which can generate fake data for most of requests.
ATLAS can also extract data from one API and use it in another.

You can supply your own data for some of the resources.
See **Mapping Resources to Database** section in [Resources](docs/resources.md) for details

---

#### Selective API Hits
You may want to load test a subset of APIs only. There are several quick ways to do that
- Exclude URLs: In settings, you can give a list of OP_KEYS for excluding URLs
- Tag Specific: (tags are the same as those given in swagger). See [Profiles](docs/profiles.md) for tagging example
    - In settings, mark ONLY_TAG_API as True
    - In `conf/profiles.yaml`, in the `tags` section, mark the tags you want to test with
- You can generate your own scenarios. More details in Scenarios section.

---

#### Manipulating Requests
ATLAS allows you to manipulate request to API. You may want to do this to:
- Change the body being sent to an API
- Change URL being hit (eg: changing Query Params in it)
- Change Other Parameters (eg: Headers)

See [Hooks](docs/hooks.md) for details on how to do this, and various examples for same

---

#### API Ordering

If you wanted to over-write ATLAS AI API ordering, you can do so.
In `conf/conf.py`, change `SWAGGER_OPERATION_DEPENDENCIES`.

This setting is a list of 2-element tuple where it ensures that first element is always hit before second element.
Each element represents OP_KEY of Swagger Operation.
OP_KEY is simply "METHOD url" for any Swagger Operation
OP_KEY for all swaggers can be obtained in `conf/routes.py` which is generated via `atlas generate_routes`

---

#### Generate Custom Scenarios
By default, ATLAS will hit all APIs in an order pre-determined by its AI.
You may wish to specify a custom workflow or scenario.

ATLAS Provides such ability
- Writing custom scenario and linking it to profiles
- Profiles can have multiple scenarios associated with them
- If needed, can over-write default scenario

See `Creating Custom Scenario` section in [Use cases](docs/uses_cases.md) for more details


Example Project
===============

- After installing ATLAS, run `atlas example <example_name>` (To know possible examples you can run `python atlas example --help`)
- Switch to Project, and you will steps to run Server and Load Test


Contributing to ATLAS
=====================

Please see [Contribution Guide](CONTRIBUTING.md)
