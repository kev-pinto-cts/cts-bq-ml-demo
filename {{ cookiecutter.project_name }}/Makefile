PROJECT_ID ?= {{ cookiecutter.gcp_project_id }}
REGION ?= {{ cookiecutter.region }}

PROJECT_NUMBER ?= $$(gcloud projects list --filter="project_id:${PROJECT_ID}" --format="value(PROJECT_NUMBER)")
TF_BUCKET ?= tf-state-bq-ml-demo-${PROJECT_NUMBER}
BUCKET_EXISTS ?= $$(gcloud storage buckets list gs://${TF_BUCKET}* --limit=1 --format="(name)"| wc -l)


.PHONY: $(shell sed -n -e '/^$$/ { n ; /^[^ .\#][^ ]*:/ { s/:.*$$// ; p ; } ; }' $(MAKEFILE_LIST))
.DEFAULT_GOAL := help

help: ## This is help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

init: ## This is init
	@gcloud config set project ${PROJECT_ID}
	@if [ ${BUCKET_EXISTS} -eq "0" ]; then \
        echo "Bucket ${TF_BUCKET} does not Exist and will be created"; \
		gcloud storage buckets create gs://${TF_BUCKET} --default-storage-class=nearline --location=${REGION}; \
    else \
        echo "Bucket ${TF_BUCKET} Exists and will be used"; \
    fi
	@sed -i "s/REPLACE-ME/${TF_BUCKET}/g" ./infra/providers.tf

plan: init ## Terraform Plan
	@cd infra
	@terraform init && terraform plan
