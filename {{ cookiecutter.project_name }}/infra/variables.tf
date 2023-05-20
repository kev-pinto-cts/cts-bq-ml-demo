variable "project_id" {
  type        = string
  default     = "{{ cookiecutter.gcp_project_id }}"
  description = "GCP Project"
}

variable "region" {
  type        = string
  default     = "{{ cookiecutter.region }}"
  description = "GCP Region"
}


variable "schema_file_path" {
  type        = string
  default     = "./config"
  description = "The location of the Bigquery YAML"
}
