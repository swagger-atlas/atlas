Need and Use Case for Related Resources
=======================================

Consider the following response for `GET repo/`:

```json
    [
        {
            "user_id": 1,
            "repo_id": 1
        },
        {
            "user_id": 1,
            "repo_id": 2,
        }
        {
            "user_id": 2,
            "repo_id": 3
        }
    ]
```

Now, if we want to hit URL: `PATCH user/{user_id}/repo/{repo_id}`

Chances are that this would be successful only with combinations of (1, 1), (1, 2) or (2, 3)

If we independently store Users and Repo ID, like:
- User: {1, 2}
- Repo: {1, 2, 3}

And then try to extract the IDs from them, we may get an invalid combination like (2, 1)

This is what we mean when we say that resources are related.

In another words,
    If X and Y are related, choosing a value for X would have impact on how we can select value for Y.

This guide will help us understand how we solve this problem


Data Structure
==============

To store the values for related resources, we use hash maps with composite keys.
A composite key consists of Profile + all resources in sorted order.

For example:

    Profile "A" with resources: user, repo  would have key ---> `A:repo,user`

Payload is the set of array containing string containing all resource values in order of sorted keys

    "user": 1, "repo": 2 would have value `[2, 1]`    (Repo comes first in lexical sorting)

Final `hashMap` may look like this:
```js
{
    "a:repo,user": Set({[1, 1], [2, 1], [3, 2]})
}
```


Inserting Values in HashMap
===========================


Insertion is done by calling `insert()` method.
To insert the relation, we provide
- Profile name
- Object containing resource keys with their values
  Example:
  ```js
  {
    "repo": Set {1},
    "user": Set {1}
  }
  ```

To insert multiple values, call `insert()` multiple times

###### Notes on Merging
If we have resource (A, B) and (B, C), does it imply (A, C)?
In the end, we were convinced that transitive property does not hold true.

Consider for a sample Git hosting web APIs may have following resources:
- (account, repo) : `[(1, "MY_REPO"), (1, "ANOTHER_REPO"), (2, "XYZ")]`
- (account, commit): `[(1, 123456), (1, 234566777)]`

This does not however enable us to say with confidence what would be correct value for (repo, commit) would be.

Similarly, we cannot simply concat these to get (account, commit, repo)
(Cardinal product would give wrong result)


Query
=====

Query is done by calling `query()` method.

`query(["repo", "user"], "a")` --> returns all resources with profile a, and relatedResource as repo and user.
It is up to user to select appropriate entry from the list returned.


How is delete handled?
======================

Some resource values may become invalid over time of API workflow.
They are NOT removed from related Resources hashMap since that would incur high performance penalty.

They are however removed from INDIVIDUAL resources.
This means after querying relation resources, and picking a value from candidate pool,
we can quickly check that each individual value is valid.
If not, we can continue and pick another value from candidate pool, and repeat the process as necessary


Further Possible Improvements
=============================

1. Our work enables us to know in advance which related resources we might need in future.
This can enable us to only save the required resources, and we can discard the rest of them saving on memory

2. While at this stage, we do not plan to add support for delete method directly,
we can however easily add the support for removing values which have been found invalid by caller function.
This would improve the HIT ratio, and also save memory.
