output "s3_bucket_raw_name" {
  description = "Raw data S3 bucket"
  value       = module.s3.bucket_raw_name
}

output "s3_bucket_transformed_name" {
  description = "Transformed data S3 bucket"
  value       = module.s3.bucket_transformed_name
}

output "athena_database_raw" {
  description = "Athena raw database"
  value       = module.athena.database_raw_name
}

output "athena_workgroup" {
  description = "Athena workgroup"
  value       = module.athena.workgroup_name
}
