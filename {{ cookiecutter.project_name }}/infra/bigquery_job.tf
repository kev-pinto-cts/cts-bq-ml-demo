resource "google_bigquery_job" "job" {
  depends_on = [ google_bigquery_dataset.dataset ]
  job_id     = "job_query"

  labels = {
    "example-label" ="bq-ml-demo"
  }

  query {
    query = "SELECT state FROM [bigquery-public-data.iowa_liquor_sales.sales]"

    destination_table {
      project_id = var.project_id
      dataset_id = google_bigquery_dataset.dataset.0.dataset_id
      table_id   = "iowa-demo"
    }

    allow_large_results = true
    flatten_results = true

    script_options {
      key_result_statement = "LAST"
    }
    create_disposition=CREATE_IF_NEEDED
    write_disposition=WRITE_TRUNCATE
  }
}
