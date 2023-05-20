terraform {
  required_version = "~> 1.3"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.63.1"
    }
  }
  backend "gcs" {
    bucket = "REPLACE-ME"
    prefix = "terraform/bqml"
  }
}

provider "google" {
  # Configuration options
  project = var.project_id
  region  = var.region
}
