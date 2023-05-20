locals {
  default_labels = {
    "department" : "data-engineering"
  }
  bigquery           = yamldecode(file("${var.schema_file_path}/bigquery.yaml"))
  datasets_to_create = { for ds in local.bigquery.bigquery.datasets : ds.name => ds if try(ds.create, true) }
  tables = flatten([for dataset in local.bigquery.bigquery.datasets : [
    for tbl, val in dataset.tables : merge(val, { dataset_id = dataset.name })
  ]])
}
