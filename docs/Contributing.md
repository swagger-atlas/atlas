ATLAS depends on the contributions of other developers.
We are so pleased you are interested in the same

There are many ways you can contribute to ATLAS:

- Issue bug reports on [Tracker][Tracker]
- Improve the documentation
- Add feature requests or enhancements at [Tracker][Tracker]
- Submit PR for your favorite features and/or improve on existing test case suite.
Please see contribution guidelines below for more details

[Tracker]: https://jira.jtg.tools/secure/RapidBoard.jspa?projectKey=LT


Project Setup
=====

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
======

- Indentation Styles: Prefer Spaces (4) over Tab
- Add your changes in Changelog.md
- Your commits should not decrease pylint score of any existing file.
