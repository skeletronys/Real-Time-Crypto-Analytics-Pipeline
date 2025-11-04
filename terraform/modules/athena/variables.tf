variable "project_name" {
  description = "Project name prefix"
  type        = string
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
}

variable "database_name" {
  description = "Base database name"
  type        = string
}

variable "s3_bucket_athena_name" {
  description = "S3 bucket name for Athena results"
  type        = string
}