Changelog
========

3.0.0
-----

*Breaking Changes*
- Auto-generation of OperationID naming schema logic have been changed
Impact: Custom Hooks would need to be renamed to use new Operation IDs.
This will **only** affect you if you rely on ATLAS to generate your operation IDs and use them in your hooks
If Your Swagger Schema contains Operation IDs, ATLAS will continue to respect that

*Enhancements*
- Changed default string length of randomly generated string in ATLAS to 10 from 100.

*Bug Fixes*
- Several issues which could produce cycle in ATLAS were identified and fixed
- `ALL OF` property is now respected while generating resources


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

v2 is incompatible with v1 since it changes how profiles are selected and loaded internally.
However, you should be able to simply migrate to v2 without any change on your end

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
