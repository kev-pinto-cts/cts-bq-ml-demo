"""Check  that the project name is valid."""

import re
import sys

MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"

project_name = "{{ cookiecutter.project_name }}"

if not re.match(MODULE_REGEX, project_name):
    print(f"ERROR: {project_name} is not a valid Python module name!")
    print("Module names can contain only letters, numbers and underscores.")

    # exits with status 1 to indicate failure
    sys.exit(1)
