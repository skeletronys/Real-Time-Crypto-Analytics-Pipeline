# Marts Crypto Metrics Table (DBT create, here placeholder)

resource "aws_glue_catalog_table" "fct_crypto_metrics" {
  database_name = var.database_name
  name          = "fct_crypto_metrics"
  description   = "Fact table with crypto metrics and volatility"

  table_type = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL     = "TRUE"
    "table_type" = "ICEBERG"
    "comment"    = "Managed by DBT"
  }

}

variable "database_name" {
  description = "Glue database name for marts"
  type        = string
}