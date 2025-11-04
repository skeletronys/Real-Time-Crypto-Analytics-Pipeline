# Root main.tf - orchestrates all modules

module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
}

module "athena" {
  source = "./modules/athena"

  project_name          = var.project_name
  environment           = var.environment
  database_name         = "crypto_analytics"
  s3_bucket_athena_name = module.s3.bucket_athena_name
}

module "table_crypto_prices" {
  source = "./modules/tables/raw"

  database_name      = module.athena.database_raw_name
  s3_bucket_raw_name = module.s3.bucket_raw_name
}
