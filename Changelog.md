Changelog
========

2.2.1
-----

*Bug Fixes*
- Custom Global Configuration was being over-ridden by `dist` script. It is now fixed
- Add an enhancement to improve delete operation ordering.
Operation deleting the resource is now executed after all operations depending on the resource are finished.
- Fixed Artillery byte provider


2.2.0
-----

*Features*
- Aliases (Resource synonyms) are now used at time of ordering, as well as at run time when resources are fetched dynamically
- Made several resource auto-detection features configurable via settings

*Bug Fixes*
- Fix Artillery if it encounters "null" in response


2.1.1
-----

*Bug Fixes*
- Fix Artillery Headers
- Fix dummy request object generation
- Fix breaking of Artillery Parser when it encountered Null value in response


2.1.0
-----

*Features*
- Added a command line option to create new examples - `python atlas example <example_name>`
- Added Pet-store example


2.0.3
-----

*Bug Fixes*
- Correctly parse array response
- Fix issue with extraction of resources from response body


2.0.2
-----

- Security Updates. Updated Requests library where it removes Authorization header from requests redirected from https to http on the same hostname. (CVE-2018-18074)


2.0.1
-----

- Comprehensive Documentation Updates.


2.0.0
-----

*Features*
- Multiple Profiles support. Now, each VU is picked randomly from one of the profiles


1.2.1
-----

- Comprehensive Documentation Updates


1.2.0
----

*Features*
- Automatically mark IDs and Slugs as Read only in references
- Readme updates, mainly regarding resource mapping and resource hooks


1.1.0
---

*Features*
- Dist Command Output message enhancements
- Data Provider to pick up 10 values from List API results
- Change default metric of Artillery from arrivalCount to arrivalRate
- Cache is now always created from scratch
