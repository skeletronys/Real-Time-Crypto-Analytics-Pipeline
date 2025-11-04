# Raw Crypto Prices Table

resource "aws_glue_catalog_table" "crypto_prices" {
  database_name = var.database_name
  name          = "crypto_prices"
  description   = "Raw crypto price data from CoinGecko"

  table_type = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL              = "TRUE"
    "parquet.compression" = "SNAPPY"
  }

  storage_descriptor {
    location      = "s3://${var.s3_bucket_raw_name}/raw/crypto_prices/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "ParquetHiveSerDe"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"

      parameters = {
        "serialization.format" = "1"
      }
    }

    columns {
      name    = "symbol"
      type    = "string"
      comment = "Cryptocurrency symbol"
    }

    columns {
      name    = "price_usd"
      type    = "double"
      comment = "Price in USD"
    }

    columns {
      name    = "market_cap_usd"
      type    = "double"
      comment = "Market cap in USD"
    }

    columns {
      name    = "volume_24h_usd"
      type    = "double"
      comment = "24h trading volume in USD"
    }

    columns {
      name    = "price_change_24h_pct"
      type    = "double"
      comment = "24h price change percentage"
    }

    columns {
      name    = "last_updated_at"
      type    = "bigint"
      comment = "Unix timestamp of last update"
    }

    columns {
      name    = "fetched_at"
      type    = "string"
      comment = "ISO timestamp when data was fetched"
    }

    columns {
      name    = "source"
      type    = "string"
      comment = "Data source (coingecko)"
    }
  }

}

# Variables for this table
variable "database_name" {
  description = "Glue database name"
  type        = string
}

variable "s3_bucket_raw_name" {
  description = "S3 bucket name for raw data"
  type        = string
}