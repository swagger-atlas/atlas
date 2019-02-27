Changelog
========


8.1.0
-----

*Features*
- Commands requiring `type` now set `Artillery` as default
- Added `atlas` console script. Now commands can be run via `atlas <>`
Docs have been updated to reflect this change
- Added a wrapper for Artillery Load Test. Can simply run test by using `atlas run`

*Bug Fixes*
- Removed redundant code
- Fixed dist command which was failing due to `TypeError`


8.0.2
-----

- Arrays are now completely supported by Relationship resources


8.0.1
-----

- Comprehensive Documentation updates for User guide
- Added Reference section for technical concepts
- Several Internal functions and classes have been given docstrings


8.0.0
-----

One of the biggest releases up to date.
It is recommended you create a new project with this release and copy your old settings here.

*Breaking Changes*
- Settings have been refactored.
Several settings have been renamed, and some of the settings now reside in `conf/conf.py`.
- Several Setting Inputs have been changed
- Swagger Operation ID naming schema has been changed

*Features*
- Added option for custom scenarios
- All Swagger Operation inputs are now consolidated in one format
- Can generate OP_KEY for all Swagger routes by using `python manage.py generate_routes`
- Several Swagger Keys can now be used as field names in References
- Added Dummy JSON Provider (type: string, format: json --> returns {})
- Added Regex Pattern support in Providers for string
- Add support for adding File Sub types from Hooks
- Comprehensive documentation updates

*Bug fixes*
- Fix `Enum` options in provider if their choice was false-y value
- String and URL Providers enhanced to correctly support MAX characters
- File Provider fixed
- Resource Values were deleted even if their API was failing. This has been fixed


7.0.0
-----

*Features*
- Added a "related relationship" feature, which allows multiple dependent resources to use data which makes sense together


6.0.0
-----

*Features*
- Added InfluxDB Integration to store raw data
- Integrated Graphana dashboards for beautiful statistics


5.1.2
-----

*Features*
- Added more validations
- Updated documentation


5.1.1
-----

*Features*
- Add basic swagger validations. This will automatically run as part of `dist` process
- Add basic hints on integration process, and added documentation for bets practices in integration.

*Bug fixes*
- Pre-existing resource names in URL params in Swagger were not given their own references. This has been resolved


5.0.1
-----

Updated Pet-store example to reflect all new changes


5.0.0
-----

*Breaking Changes*
- Changed the following settings name:
    1. `URL_PARAM_RESOURCE_SUFFIX` to `SWAGGER_URL_PARAM_RESOURCE_SUFFIXES`
    2. `PATH_PARAM_RESOURCES` to `SWAGGER_PATH_PARAM_RESOURCE_IDENTIFIERS`
    3. `REFERENCE_FIELD_RESOURCES` to `SWAGGER_REFERENCE_FIELD_RESOURCE_IDENTIFIERS`
    4. `ORDERING_DEPENDENCY` to `SWAGGER_OPERATION_DEPENDENCIES`
These new identifiers mark settings clearly Swagger settings
Also, it reflects better that these settings reflect that they are plural values


4.1.0
-----

*Features*
- Write Auto-generated Operation ID to Swagger
- Add the option to allow resources to be not updated at run-time


4.0.0
-----

*Breaking Changes*
- Added new settings in Template
- Changed Conf, Build and Dist folder structures
- Changed Profile and Operation Hooks Interface

*Migration Guide*
1. Create a new project with ATLAS
2. Copy Swagger and Profiles
3. Use new hook registration format for operation hooks
4. Change the profile hooks as needed

*Features*
- Collect Stats for each endpoint and write them to raw file
- Allow end-users to add ordering in operations through settings


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
-----

*Features*
- Automatically mark IDs and Slugs as Read only in references
- Readme updates, mainly regarding resource mapping and resource hooks


1.1.0
-----

*Features*
- Dist Command Output message enhancements
- Data Provider to pick up 10 values from List API results
- Change default metric of Artillery from arrivalCount to arrivalRate
- Cache is now always created from scratch
