variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key"
  type        = string
  sensitive   = true
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "crypto-analytics"
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
  default     = "dev"
}