ATLAS depends on the contributions of other developers.
We are so pleased you are interested in the same

There are many ways you can contribute to ATLAS:

- Submit bug reports on [Tracker]
- Improve the documentation
- Add feature requests or enhancements at [Tracker]

[Tracker]: https://jira.jtg.tools/secure/RapidBoard.jspa?projectKey=LT

Our workflow is pretty simple.
- Make your changes, and submit us a PR
- In the Commits as well as PR, do mention the issue id(s)
- Make sure you update CHANGELOG.md in "UPCOMING RELEASE" section with changes you mentioned in the format:
`<commit-id> #<pull-request-id> brief explanation (@<handle>)`
An example would be: `a0e34567 #45 fix typo in docs on resources (@someone)`


Project Setup
=============

1. Create a Virtual Environment
    - Run `virtualenv <path/to/virtualenvs/atlas> -p <python3.x>`
     (Replace <variables> with your own versions). Python should be 3.6+
    - `source <path/to/virtualenvs/atlas>/bin/activate` to activate this

2. Run requirements
    - `pip install -r requirements.txt`
    - See `http://initd.org/psycopg/docs/install.html#build-prerequisites` in case there are issues with Postgres Client

3. Set up Pylint Hook
    - Create a file under .git/hooks/ with name pre-commit
    - Add to that file:
       ```bash
        #!/usr/bin/env bash
        /path/to/git-pylint-commit-hook --pylint /path/to/pylint --pylintrc pylint.rc
       ```
    - Update the permissions by `chmod +x .git/hooks/pre-commit`

    You can run pylint anytime by using `pylint --rcfile=pylint.rc <file_path>`


Coding Guidelines
=================

Python:
- Indentation Styles: Prefer Spaces (4) over Tab
- Your commits should not decrease pylint score of any existing file.
- Prefer f-strings in Python
- Add Test cases for any change or new feature as required in `tests/`

Javascript:
- Prefer Template Strings in Javascript
- Add test cases in `js_tests/`


Testing
=======

For testing, run
- `py.test --cov=atlas/` for python module (We use [pytest](https://pytest.readthedocs.io/en/4.3.0/))
- `npm run coverage` for JS Modules (We use [jest](https://jestjs.io/docs/en/getting-started.html))


Code of Conduct
===============

Please refer to [Code of Conduct](CODE_OF_CONDUCT.md)
