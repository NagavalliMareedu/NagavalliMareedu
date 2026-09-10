output "cloud_run_url" {
  description = "Deployed Cloud Run service URL."
  value       = google_cloud_run_v2_service.api.uri
}

output "runtime_service_account" {
  description = "Least-privilege runtime service account."
  value       = google_service_account.runtime.email
}

output "artifact_registry_repository" {
  value = google_artifact_registry_repository.ai_apps.name
}
