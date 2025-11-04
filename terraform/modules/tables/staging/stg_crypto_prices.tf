# Staging Crypto Prices Table (DBT will create this table, this is just a placeholder)

# This is a view table created by DBT, so we don't need to create it here.
# But if you want to have a reference:

resource "aws_glue_catalog_table" "stg_crypto_prices" {
  database_name = var.database_name
  name          = "stg_crypto_prices"
  description   = "Staging layer - cleaned crypto price data"

  table_type = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL              = "TRUE"
    "table_type"          = "ICEBERG"
    "comment"             = "Managed by DBT"
  }

  # DBT will manage the scheme, so there is minimal information here.
}

variable "database_name" {
  description = "Glue database name for transformed data"
  type        = string
}