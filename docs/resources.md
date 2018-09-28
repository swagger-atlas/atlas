Resources
======

ATLAS comes in with a battery of providers, which can fake data for almost any Swagger configuration.
However, sometimes, a random fake data is not what we want.

For example, primary keys of Tables, tokens, etc are some entities which we want to be realistic, and extracted from Project DB itself.
These such entities are collectively known as "resources" in ATLAS.


Identification of Resources
========

Explicit
------
- User can specify resources in SWAGGER file explicitly by using `resource: <>` property
- This could be specified in any Parameter or reference
- Users could manually edit the Swagger file, or change their project documentation for same
- Users could also directly add the resources in `conf/resource_mapping.yaml` file

Automated
-----
We understand that tagging all resources for the sake of ATLAS alone is something most developers would be averse to for various reasons.
That is why, we developed limited but powerful intelligence which tries to parse your swagger and auto-generate the resources
- We look for resources in Parameters and References
- If there is any explicit resource, we go for it
- Else, we try to reason which entities could be faked, and which needs to be tagged resources.

You can run `python manage.py generate` which would collate the explicit resources with generated resources.
You can check the output in `build/resource_mapping.yaml`
- If we miss any resources in the automation, do let us know!


Mapping Resources to Database
========

- Once resources are identified, we need to fetch their data from DB.
- For this, we need to map the resources to relevant source
- Resource Mapping file serves this purpose

Resource Mapping File
------
- The final resource mapping file is available in `build/resource_mapping.yaml`
- It is combination of `conf/resource_mapping.yaml` and Automated Generation of resources
- This file contains resource declarations as well as their data source.

A very simple mapping could look like:
```
resource_a:
    table: A
```
This roughly translates to "select id from A" query and store the results for resource_a.


Various Options for Resource Mapping Files are:
- source: Tells what the source for this resource is. Possible values are `table`, `script`. Default value is `table`

Table Source Options
- table: Table Name
- column: Column Name. Defaults to id
- filters: Any filters you want to add
- sql: Ignores all of above options, and write your own custom sql query
- mapper: Post-processing function you want to run. Default mapper takes the SQL Output as input (which is list of tuples) and flatten them up.


Script source options
- func: Function Name. Must be declared in `conf/resource_hooks.py` file
- args: Argument List
- kwargs: Keyword argument list


Misc Options
- resource: Inherit the resource definition of another resource. You can then selectively over-write the keys or keep them exactly the same
- def: Denotes dummy resource. No data is fetched for it.


Important Considerations
- While defining the resources, you can use `{<var_name>}` syntax. This var_name is picked up from your profiles.yaml file.
- So, your resources could be personalized to each profile type

You can fetch data for resources using `python manage.py fetch_data`
This will create resources folder in build
Each file would be <profile_name>.yaml and each file would contain your resources fetched for that profile

**While defining resource mapping file is ideal, it could be an arduous task to do same for potentially hundreds of resources.**
That's why we have implemented something called Workflow


Workflow
=======
Resource Mapping file need not contain the DB mapping for each and every resource, if we can extract and use the resource during run-time itself.
For example, if you have exposed CREATE API for resource A, and then some other API use the resource A.
Then ideally it should be possible for us to use the results of CREATE API and apply the results in other APIs as needed.
This concept is known as Workflow.

Workflow reduces the need for defining all resources, (and now you need to only define the resources which are consumed but never produced)

Workflow depends on following:
- Program can determine APIs consumptions and productions regarding resources correctly
- It can then create the graph showing correct dependencies
- Using this graph, it can order the API workflow
- And finally, it can retrieve and store the results of your API to resources correctly for relevant profiles.

ATLAS have support for each of these steps, and does not require any User intervention at all!!
However, we would like to see the feedback from the users if they face any problems during Workflow execution to help us improve on our algorithm

Workflow design is covered implicitly under the BUILD command, and does not require any additional action from user.
