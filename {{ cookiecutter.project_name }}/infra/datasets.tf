resource "google_bigquery_dataset" "dataset" {
  for_each = local.datasets_to_create

  dataset_id                 = each.key
  project                    = var.project_id
  friendly_name              = try(each.value.friendly_name, each.key)
  description                = try(each.value.description, each.key)
  location                   = try(each.value.location, "EU")
  delete_contents_on_destroy = each.value.delete_contents_on_destroy
  labels                     = merge(local.default_labels, try(each.value.labels, {}))
  max_time_travel_hours      = try(each.value.max_time_travel_hours, 168) # Max is 7 days

  dynamic "default_encryption_configuration" {

    for_each = try(each.value.cmek_key, false) ? ["cmek"] : []

    content {
      kms_key_name = each.value.cmek_key
    }
  }
}
