# `{{ cookiecutter.project_name }}` README

This repository contains the folder layout and Terraform configuration for the
sandbox development of the {{ cookiecutter.project_name }} project.

## Prerequisites

-   A GCP account.
-   (Optional) for GitHub (needed for Terraform Cloud): a GitHub API token with
    `repo` access. (For testing, it should also be able to delete repos.)

## Bootstrapping

Clone this repository and open its devcontainer. This should give you an
environment with `gcloud` and `terraform` installed, along with other
tools.

All configuration files in this repository are prepopulated with the correct
information since you've already used the cookiecutter to generate the
repository structure.

You now need to build out the initial `demo` project from the terminal. This
is the project which contains Atlantis, which will then be used to deploy the
remaining projects programmatically using a CI/CD model.

Ensure that your `gcloud` credentials have been set with
`gcloud auth application-default login`, then run:

```sh
cd bootstrap
../scripts/post_create.sh
cd ..
```

Finally, commit the local code to the newly-created repository:

```sh
scripts/post_deploy.sh
```

At this point you can work exclusively through a Git-based workflow with no
further manual infrastructure changes.

## Testing

The entire infrastructure can be tested using Test Kitchen. After setting your
`gcloud` credentials, simply run `kitchen test` to stage the environment, run
integration tests, and then tear it back down assuming that all tests pass.

To write new tests:

1.  Add a new suite to `.kitchen.yml` (if testing a new environment).
2.  Add tests to `test/integration/<env/path>/default.rb`.
