variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "region" {
  description = "GCP region for resources and Vertex AI."
  type        = string
  default     = "us-central1"
}

variable "repository_name" {
  description = "Artifact Registry repository."
  type        = string
  default     = "ai-apps"
}

variable "service_name" {
  description = "Cloud Run service name."
  type        = string
  default     = "gcp-ai-api"
}

variable "container_image" {
  description = "Container image deployed to Cloud Run."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "vertex_model" {
  description = "Gemini model available in the selected Vertex AI region."
  type        = string
  default     = "gemini-2.0-flash"
}

variable "min_instances" {
  type    = number
  default = 0
}

variable "max_instances" {
  type    = number
  default = 5
}

variable "allow_unauthenticated" {
  description = "Allow unauthenticated Cloud Run invocation for demo use."
  type        = bool
  default     = false
}
