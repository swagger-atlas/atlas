Resource Deletion
-----------------

Over the course of API workflow, some resource values would become invalid.
This mostly happen due to call to DELETE operations.

When we execute such APIs, it is imperative that we delete such values from ATLAS local storage.

#### What to delete

Consider API: `DELETE /user/{id}/repo/{id}`

In this, we are reasonably sure that we are deleting REPO and not USER resource.
In fact, going over several API endpoints across several projects,
in addition to OpenAPI and REST best practices,
we have found that resource which comes at very end of URL in DELETE requests
is in fact the *only* resource to be deleted.

That is our logic too.

#### When to delete

Resources could be deleted at two times:
- Before Request is executed:
    As soon as we become aware that we need to hit the API,
    we delete the value for the requisite resource
- After Response:
    In another approach, we wait till we get success response,
    and then only delete the resource.

Latter approach, which deletes after response has been fetched, has one major flaw.

Consider the following:
```
Resources:
    A: {1, 2, 3}
```


And the API workflow:
```
GET A/{id}
DELETE A/{id}
```

Now, consider that for delete OP for Virtual User 1 (VU 1), we selected `A=2`.
Till the time, VU 1 is waiting for the response,
any other VU is free to select A = 2 also for their executions.

This would result in race conditions, where if other VUs execute before VU 1,
their OP would be successful, else it would be failure.

This is why we delete *before request*.
This takes out `A=2` from candidate pool for other APIs which need to use A resource.

However, this necessitates the rollback mechanism.
If we delete the resource, and API is successful, then there is no issue.
But, if we delete the resource, and API returns failure, it can cause some issues.
(Esp. if resource has only few viable candidates)
