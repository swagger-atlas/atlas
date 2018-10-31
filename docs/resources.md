Resources
======

ATLAS comes in with a battery of providers, which can fake data for almost any Swagger configuration.
However, sometimes, a random fake data is not what we want.

For example, primary keys of Tables, tokens, etc are some entities which we want to be realistic, and extracted from Project DB itself.
These such entities are collectively known as "resources" in ATLAS.


Identification of Resources
===========================

Automated
-----
Resources are largely identified via automated system.
- We look for resources in Parameters and References
- If there is any explicit resource, we go for it. (See Manual Section below)
- Else, we try to reason for which entities data could be faked, and which needs to be tagged resources.

You can run `python manage.py detect_resources` which would collate the explicit resources with generated resources.
You can check the output in `build/resource_mapping.yaml`
- If we miss any resources in the automation, do let us know!


Explicit/Manual
---------------
We do provide mechanism to manually mark the resources in Swagger by add `resource` keyword in relevant entity.

*Example*
```yaml
- in: path
  name: id
  resource: student     # We marked this as Student Resource in Swagger, and our Automation system will respect that
  required: true
```


Mapping Resources to Database
========

- Most of resources thus identified would have their data fetched during execution of API workflow itself (See Workflow section below)
- However, there may be some resources for which we cannot get their data in Workflow (eg: APIs which do not have any Create/List APIs and have manual creation/updation process)

- For them, we can have data pre-populated in the system
- For this, we need to map the resources to relevant DB source
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


**Source**
Tells what the source for this resource is. Possible values are `table`, `script`. Default value is `table`.
Table source would construct an SQL query to fetch the data from given table

**Table Source Options**
- table: Table Name (Required)
- column: Column Name. Defaults to `id`
- filters: Any filters you want to add
- sql: Ignores all of above options, and write your own custom sql query
- mapper: Post-processing function you want to run. Default mapper takes the SQL Output as input (which is list of tuples) and flatten them up. Mapper function is defined in `conf/resource_hooks.py`

In `Filters` and `sql` you can use context variables from `profiles.yaml` file to customize your data for a single profile. See SQL Example below

*Example Snippet*
```yaml
student:
    table: students_student
    # Query would be "select id from students_student;" and this query result would be processed to return a flat list of IDs

invitation:
    table: invitations_invitation
    column: token
    # Query would be "select token from invitation_invitation;" and this query result would be processed to return a flat list of IDs

offer:
    table: offers_offer
    filters: is_active=true and status=1
    # Query would be "select id from offers_offer where active=true and status=1;" and this query result would be processed to return a flat list of IDs

courses:
    sql: select id from courses_courses c join student_courses s on c.id = s.course_id where s.student_id = {id}
    # Here ID, would be picked and templated from conf/profiles.yaml file.
    # If ID is defined as 5 for example, query would be: "select id from courses_courses c join student_courses s on c.id = s.course_id where s.student_id = 5;"

auth:
    table: users_token
    mapper: encode
    # Query would be "select id from user_token;" and this query result would be encode(<result_of_sql_query>)
```


**Script source options**
- func: Function Name. Must be defined in `conf/resource_hooks.py` file. This is required argument
- args: Argument List. Optional
- kwargs: Keyword argument list. Optional

*Example Snippet*
__resource_mapping.yaml__
```yaml
resource_name:
    source: script
    func: my_func_name
    args:
        - 1
        - 2
    kwargs:
        a: 1
```

__resource_hooks.py__
```python
def my_func_name(arg_1, arg_2, a):
    return [arg_1 + arg_2 + a, arg_1, arg_2]

# Note: Function MUST return a list, even if it single value.
```

**Misc Options**
- resource: Inherit the resource definition of another resource. You can then selectively over-write the keys or keep them exactly the same
- def: Denotes dummy resource. No data is fetched for it.

*Example - Resource Inheritance*
```yaml
animal:
    table: animals_animal

pet:
    resource: animal
    # Exactly same as animal resource

cat:
    resource: pet
    filters: type='cat'
    # Same as Pet Resource with filter over-ridden
```

*Example - Dummy Resource*
```yaml
forums:
    def: <something>
    # This resource WILL not be parsed EVEN if other keys are found
    # These resources are generated at run-time during workflow itself, rather than pre-compiled in cache
```

**Globals**
- If you have properties which you would like to execute to all resources, you can define it in `$globals`

*Example*
```yaml
$globals:
    filters: is_active=true

user:
    table: users_user
    # Use the global filter

admin:
    table: users_user
    filters: is_active=true and role=2
    # Use its own filter rather than global
```

You can fetch data for resources using `python manage.py fetch_data`
This will create resources folder in build
Each file would be <profile_name>.yaml and each file would contain your resources fetched for that profile

- Resource Defined in Resource Mapping file as TABLE or SOURCE resources are pre-compiled.
This ensures that even if there are no APIs constructing these resources, we would always have a valid data for them.
Pre-compiled resources *do* update  during workflow also
- Resources Marked with DEF are only created and updated during run-time.


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
