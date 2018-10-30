Swagger Best Practices
================

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
- Swagger, and by extension ATLAS does not support parameters which are dependent on each other within single API.

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


Responses
---------

[Swagger responses](https://swagger.io/docs/specification/2-0/describing-responses/) are used by ATLAS for ensuring that request was successful, and to update dynamic resource caches.

- Make sure all responses are documented with correct status code. You can use `default` response to cover all fallback cases
- Response body should be a reference, and not manual description.


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
