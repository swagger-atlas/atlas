Use Cases
=========

This guide will explain some of the common use cases which are encountered while integrating the ATLAS with your project.
Some of these use cases are hinted while integrating your project.

This guide will also explain best practices for writing Swagger

Please also see these guides:
- [Profiles](profiles.md)
- [Resources](resources.md)


Authenticating APIs
-------------------

It is possible to provide Authentication to APIs.

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

> If some APIs failed due to Auth Error (401), ATLAS will give warning

Hitting Selective APIs
----------------------

There are two ways to select which APIs to hit:

#### Tagging the APIs

You can specify tags in Swagger, and then mark them in Profiles.
This selects only those APIs which follow the tag schema.

This allows you to control the APIs at profile level

Profiles example:
```yaml
<profile_name>:
    <other_details>
    tags:
        tag_1
        tag_2
```

Also, mark `ONLY_TAG_API` as True in settings file.

#### Excluding the APIs

You can mark specific URLs to be not hit. This is a list of OP_KEYs
This is global level setting, and affects all of your profiles

This is available in `EXCLUDE_URLS` Settings in `conf/conf.py`

Each OP_KEY is "METHOD url" (eg: "GET /users/").
A complete list of OP_KEY can be obtained in `conf/routes.py` file generated via `python manage.py generate_routes`


Creating Custom Scenarios
-------------------------

It is possible to create own custom scenarios, and then link them to profiles.

To create a scenario, you need to enter it in `conf/conf.py` file.
A single scenario entry consists of name of scenario and All operations which it should execute in order

See Linking Scenarios to Profile section in [Profiles](profiles.md) for detailed example of same

###### Caveats
- Each Operation must be a valid entry
- Each scenario must be linked to at least single profile

*Profile Link Example*
```yaml
<profile_name>:
    scenarios:
        - my_scenario_1
```


Getting `Resource Pool Not Found/ Provider Check Failed` Error
--------------------------------------------------------------

Resources are dynamic entities which are marked and used by ATLAS.
To know more about them, please see [Resources](resources.md)

There are multiple ways in which these are created:

#### No APIs which produce Resources

There are no APIs which returns the resources we want.
This could be fixed by mapping the resource in `resource_mapping.yaml`

#### API returning resources is empty

Sometimes, the API which returns the response are empty.
This is sometimes due to ATLAS integration, and other times due to Server issues.
The easiest way is to fix is to map the resource in `resource_mapping.yaml`

#### API returning resources throws error

API responsible for returning resource is producing error.

There are multiple ways this could happen
- Swagger does not reflect the Server Request Body. Solution: Update Swagger
- Swagger does not capture the validations required by server.
Solution: Use `conf/artillery/hooks.py` file to update the request body to update the Request body


Swagger Best Practices
======================

Base Path
---------

Make sure that `schemes`, `basePath` and `host` are correctly fulfilled.

*Example*:

```yaml
basePath: /api
schemes:
    - http
host: localhost:8080
```

**Tips:**
- You can over-ride these settings in `settings.py`
- If you are using a tool to generate swagger, most of tools are configurable to generate these arguments correctly

> If this is missing in Swagger, it will be validated

Definitions
-----------

[Definitions](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#definitionsObject) is extremely useful concept in Swagger and we rely heavily on them for ATLAS.
If you are using Swagger generator, make sure it is one which do generate definitions.

In Django DRF, for example, definitions would correspond to Serializer.

Some best practices for definitions:
- Make sure relevant fields are marked `readOnly` true.
- If a field is limited to specific choices, it should be marked as ChoiceField, with all choices explicitly defined. In Swagger, you can do this by using `enum` keywords.
- Keep to conventional standards for identifying primary resources, like `id`, `pk`, `slug` etc.
- When defining relationship between two references, do this by either:
    - Complete Reference nesting (See below example)
    - Pointing to just primary key of another reference with naming schema of `<ref_name>_id` (or similar). See example

*Nested Example Snippet*
```yaml
Tag:
    id: <>
    name: <>

Category:
    id: <>
    name: <>

Pet:
    id: <>
    tag:
        $ref: '#/definitions/Tag'      # This is complete nesting. Tag would be expanded to full Tag definition
    category_id: <>                    # This is just using primary key of another reference.
```

**Advanced Usage and Tips**
- Most of time, if your tool is correct, you should have a correct Swagger representation for definitions. And if definition is not correct, it could be a sign of improper REST practices in code
- If you are not willing/unable to correct your code to match References Best Practices, you can manually edit Swagger to mark `resources` or `readOnly` properties.
- If you are using unconventional keys to mark Primary keys in your definitions, you can edit `SWAGGER_REFERENCE_FIELD_RESOURCE_IDENTIFIERS` in `conf/conf.py` to add your own.

*Manual Resource Example Snippet*
```yaml
Organization:
    id:     <>
    name:   <>

Order:
    id: <>
    organization:
        type: int64
        resource: organization          # Manually map this field to Organization resource
        required: true
```


Parameters
----------

In Swagger, you should document all parameters required by API to operate.
[Introduction to Swagger Paramaters](https://swagger.io/docs/specification/2-0/describing-parameters/)

**General Tips**
- You should document ALL parameters which are consumed by an API. This *do* include Query Parameters and Header Parameters
- If you are using Swagger Generation tools, make sure your code is written in compliance with it. Most of these tools would be only able to pick Parameters which are given in a standard format.
- Swagger, and by extension ATLAS does not support parameters which are dependent on each other within same API.

**Path Parameters Best Practice**
- Your documentation tool would generate this parameter based on your URL Path. (See example below)
- Your URL Param must be either self-descriptive or follow REST Resource standards
- Rest Resource names should match with definition names whenever possible

*Example of URL Path Param*
```
URL --> /student/:id

Would result in:

- in: path
  name: id
  required: true
  type: integer

Further, based on URL, we would mark its resource as "student", since this ID appears just after student
```


*Example of self-descriptive Param Name*
```
URL --> /archive/:category_id/

Would result in:

Would result in:

- in: path
  name: category_id
  required: true
  type: integer

Further, based on URL, we would mark its resource as "category", since this is self-descriptive
```


**Query Parameters Best Practice**
- Do document all query parameters. See Django DRF Specific Tips section for specific tips
- If a query parameter is required, explicitly mark that in Swagger


**Body and Form Parameters**
- If API consumes Body, make sure it is documented in swagger
- Define `consumes` type correctly. Default is `application/json`
- Make sure that if it is consuming body, body reference is defined in definitions rather than re-defining it.

**Advanced Usage**
- If you are using unconventional Identifiers to mark the Primary keys, you can change the following settings in `conf/conf.py`:
    - `SWAGGER_URL_PARAM_RESOURCE_SUFFIXES` (for self-descriptive param names)
    - `SWAGGER_PATH_PARAM_RESOURCE_IDENTIFIERS` (stand-alone param names)

> For Path parameters, ATLAS validates whether resources are present in definition

Responses
---------

[Swagger responses](https://swagger.io/docs/specification/2-0/describing-responses/) are used by ATLAS for ensuring that request was successful, and to update dynamic resource caches.

- Make sure all responses are documented with correct status code. You can use `default` response to cover all fallback cases
- Response body should be a reference, and not manual description.

> For response, ATLAS checks for at least one valid response, and valid definitions


Django DRF Specific Tips
------------------------

If you are using Django DRF, and then using swagger generator, then these tips would be useful.

- Rely on `ViewSets` and `GenericAPIView` than simple `APIViews`.
- Only expose Methods you mean to. For example, a complete `ViewSet` exposes 5 CRUD Operations, make sure you want them all.
- Use Routers with Viewsets to generate standard URL schemas. If you use manual URL Schemas, make sure you adhere to best practices.
- Rely on `FilterBackends` rather than manual code for Query Parameters

*Don't*
```python
def get(request):

    # Avoid this kind of programming. All arguments should be in Filters.
    arg = request.GET.get('some_arg')
```

We have found Swagger generators to mostly fail at these points:
- Custom Pagination: If you use custom pagination, make sure that the corresponding generated Swagger is correct.
- File Fields: Some Swagger generators simply mark File Fields in Serializers as string type which would result in incorrect implementation. You may need to explicitly mark them
- JSON Fields: To generate a JSON object, `json` should be `format` in string type.
