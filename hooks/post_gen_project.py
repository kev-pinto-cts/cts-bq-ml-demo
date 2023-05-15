import os
import sys
import shutil

REMOVE_PATHS = [
    '{% if not cookiecutter.include_terraform %} terraform_cdk {% endif %}',
    '{% if not cookiecutter.include_testdata %} testdata {% endif %}',
    '{% if not cookiecutter.include_pyspark %} pyspark {% endif %}',
    '{% if not cookiecutter.include_dbt %} dbt {% endif %}',
    '{% if not cookiecutter.include_buildimages %} build_images {% endif %}',
]
print("{{ cookiecutter.include_terraform }}")
for path in REMOVE_PATHS:
    print(path)
    path = path.strip()
    if path and os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)