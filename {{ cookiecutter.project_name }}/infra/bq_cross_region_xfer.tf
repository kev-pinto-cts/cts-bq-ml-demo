resource "google_bigquery_data_transfer_config" "bq_xfer_config" {
  depends_on             = [google_bigquery_dataset.dataset]
  project                = var.project_id
  display_name           = "bq_xfer_config"
  location               = var.region
  data_source_id         = "cross_region_copy"
  destination_dataset_id = "staging"
  # disabled             = false
  params = {
    source_project_id           = "bigquery-public-data"
    source_dataset_id           = "iowa_liquor_sales"
    overwrite_destination_table = "true"
  }
}
