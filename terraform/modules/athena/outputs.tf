output "database_raw_name" {
  value = aws_glue_catalog_database.raw.name
}

output "database_transformed_name" {
  value = aws_glue_catalog_database.transformed.name
}

output "workgroup_name" {
  value = aws_athena_workgroup.main.name
}