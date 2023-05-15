# `cookiecutter-data-engineering` README

This repo contains a template which can be used to build out new Python
packages within CTS.

## Usage

> [Cruft](https://cruft.github.io/cruft/) is fully compatible with [Cookiecutter](https://cookiecutter.readthedocs.io)
> and allows repositories to receive upstream updates from the Cookiecutter
> template repository.

1. Install `cruft` on your system (or use the provided devcontainer):

    ```sh
    pip3 install cruft
    ```

1. download the template you want to use and customise it:

    ```sh
    cruft create https://github.com/Cloud-Technology-Solutions/cookiecutter-data-engineering --skip=.git
    ```

## Pre-requisites

### Software packages
Please ensure that the following software is installed on your local machine:

- [Kind](https://kind.sigs.k8s.io/)
- [Helm](https://helm.sh/)
- [jq](https://stedolan.github.io/jq/)
- [yq](https://github.com/mikefarah/yq)


### Credentials

Service account keys are used by Airflow. They can be stored in the credentials folder which is added to the `.gitignore` file. Please ensure that the
service account key has only the required credentials. This is currently:

- BigQuery Administrator
- Storage

## Data Tooling

### Airflow

The airflow configuration is stored within `airflow_pipelines`.

Currently, this includes local tooling for airflow which can be accessed with the following commands:

- `start_local_airflow`: Starts a local instance of an airflow cluster
- `stop_local_airflow`: Stops the airflow cluster
- `connect_to_airflow`: Enables you to connect to airflow through the UI (username: admin, password: admin)

This will create a kind cluster (consisting of a number of docker containers) which can be accessed with the command `kind get clusters`

You can view the actual pods by running: `kubectl get pods  --namespace airflow` and the logs from a pod by
`kubectl logs airflow-webserver-774654c96b-x2zv8 --namespace airflow  -c webserver`. You will need to change the webserver name to match the name of your
webserver. You can also optionally add a `-f` flag to follow the logs.
