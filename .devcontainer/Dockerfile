FROM eu.gcr.io/cts-public-images-1/cts-python:latest

# Install cookiecutter and linting tools. Unlike the template, this isn't a
# real project and so doesn't use Poetry to track dependencies.
RUN pip install \
  cookiecutter \
  autopep8 \
  black
