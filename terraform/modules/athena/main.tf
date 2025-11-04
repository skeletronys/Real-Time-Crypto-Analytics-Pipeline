# modules/athena/main.tf

# Glue Catalog Database for raw data
resource "aws_glue_catalog_database" "raw" {
  name        = "${var.database_name}_raw"
  description = "Raw crypto price data"
}

# Glue Catalog Database for transformed data
resource "aws_glue_catalog_database" "transformed" {
  name        = "${var.database_name}_transformed"
  description = "Transformed crypto analytics data"
}

# Athena Workgroup
resource "aws_athena_workgroup" "main" {
  name        = "${var.project_name}-workgroup"
  description = "Workgroup for crypto analytics queries"

  configuration {
    enforce_workgroup_configuration    = false
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${var.s3_bucket_athena_name}/query-results/"

      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }

  tags = {
    Name        = "${var.project_name}-workgroup"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}