resource "aws_s3_bucket" "raw" {
  bucket = "${var.project_name}-raw"

  tags = {
    Name        = "${var.project_name}-raw"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket" "transformed" {
  bucket = "${var.project_name}-transformed"

  tags = {
    Name        = "${var.project_name}-transformed"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket" "athena" {
  bucket = "${var.project_name}-athena"

  tags = {
    Name        = "${var.project_name}-athena"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Lifecycle policies
resource "aws_s3_bucket_lifecycle_configuration" "raw" {
  bucket = aws_s3_bucket.raw.id

  rule {
    id     = "delete-old-raw-data"
    status = "Enabled"

    filter {
      prefix = "raw/"
    }

    expiration {
      days = 30
    }
  }

  rule {
    id     = "delete-athena-results"
    status = "Enabled"

    filter {
      prefix = "query-results/"
    }

    expiration {
      days = 7
    }
  }
}
