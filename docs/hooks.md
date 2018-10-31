Hooks
=====

Users can change the request being sent for testing via hooks mechanism.

To hook an API, you need to do two things:
1. Define Hook. Hook definition is a JS function with:
    - Signature `...args` where args is an array with parameters: URL, Body, Params for APIs which need body, and URL, Params for APIS which do not need one
    - It must return `args`
2. Register Hook
    - Hooks must be registered against Operation ID for a method. You can find operationID for method in Swagger

Hooks are completely optional.

Simple Hook
-----------

Open `conf/hooks.js` and write this:

```js
function testHook(...args) {
    console.log("I am a test hook");
    return args;
}

hook.register("operationId", testHook);
```

If your URL method operation ID is `operationID`, this ensures that whenever we load test, we hit this hook.


Hook with custom body
---------------------

```js
function customBody(...args) {
    let body = args[1];

    del body.a;
    del body.b;

    body.c = 1;

    args[1] = body;
    return body;
}

hook.register("myOperation", customBody);
```
