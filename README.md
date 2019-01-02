ATLAS
=======

- For those with mythological leanings, Atlas stand for the legend who carry the load of Earth on his shoulders
- For those who are dazzled with recursive structures, ATLAS is Tool for Load Analysis & Simulation
- For those who look still further (or backwards!), Simple Application for Load Testing and Analysis

ATLAS takes your Swagger, and smartly generates the code which could be used as input to various load testing tools.
Currently, ATLAS fully supports Artillery, and we have plans to incorporate for Locust Testing.


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

Do Read [Best Practices](docs/best_practices.md) for swagger practices to get the most out of ATLAS Automation systems.

---

#### Authenticating APIs
It may be possible that you need to provide Authentication Information with APIs.
With ATLAS, you can provide Header Authentication by:

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

---

#### Data Generation
- Atlas generates random fake data for most of the requests. This includes POST body data fields
- However, for some fields, ATLAS prefer to use real data.
  For example, Path Parameter if randomized give high error rate, so ATLAS would prefer that they are actual instances
  For most of this, ATLAS can infer these fields from results of previous APIs.
  However, you can specify the mapping of these fields yourself. See **Mapping Resources to Database** section in [Resources](resources.md) for details

---

#### Selective API Hits
You may want to load test a subset of APIs only. There are several quick ways to do that
- Exclude URLs: In settings, you can give a list of Regex for excluding URLs
- Tag Specific: (tags are the same as those given in swagger). See [Profiles](profiles.md) for tagging example
    - In settings, mark ONLY_TAG_API as True
    - In `conf/profiles.yaml`, in the `tags` section, mark the tags you want to test with

---

#### Manipulating Requests
ATLAS allows you to manipulate request to API. You may want to do this to:
- Change the body being sent to an API
- Change URL being hit (eg: changing Query Params in it)
- Change Other Parameters (eg: Headers)

See [Hooks](hooks.md) for details on how to do this, and various examples for same

---

#### Load Test Configuration
You should be able to edit load test configuration by following respective runner.
For Artillery see [CLI Options](https://artillery.io/docs/cli-reference/)


Creating a new Project
=====
- Create a virtual environment. We only support Python 3.5+.
- Install the Atlas Project by `pip install -e git@code.jtg.tools:jtg/atlas.git`
- Run `python atlas newproject <project-name>`
- Switch to new directory
- Follow the README of directory to customize and run your load test


Example Project
===============

- After installing ATLAS, run `python atlas example <example_name>` (To know possible examples you can run `python atlas example --help`)
- Switch to Project, and you will steps to run Server and Load Test


Contributing to ATLAS
=========

Please see [Contribution Guide](docs/Contributing.md)
