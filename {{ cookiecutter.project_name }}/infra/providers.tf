terraform {
  required_version = "~> 1.3"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.52"
    }
    {% if cookiecutter.vcs == "github" -%}
    github = {
      source  = "integrations/github"
      version = "~> 5.17"
    }
    {%- elif cookiecutter.vcs == "gitlab" -%}
    gitlab = {
      source  = "gitlabhq/gitlab"
      version = "~> 15"
    }
    {%- elif cookiecutter.vcs == "bitbucket-cloud" -%}
    bitbucket = {
      source  = "DrFaust92/bitbucket"
      version = "~> 2"
    }
    {%- endif %}
  }
  backend "gcs" {
    bucket = "REPLACE-ME"
    prefix = "terraform/bqml"
  }
}

# provider "{{ cookiecutter.vcs | replace("-cloud", "") }}" {
#   {% if cookiecutter.vcs != "bitbucket-cloud" -%}
#   token = chomp(data.google_secret_manager_secret_version.access_token.secret_data)
#   {%- endif %}
#   {% if cookiecutter.vcs == "github" -%}
#   owner = "{{ cookiecutter.repo_owner }}"
#   {%- endif %}
#   {% if cookiecutter.vcs == "bitbucket-cloud" -%}
#   username = "{{ cookiecutter.bitbucket_username }}"
#   password = chomp(data.google_secret_manager_secret_version.access_token.secret_data)
#   {%- endif %}
# }
