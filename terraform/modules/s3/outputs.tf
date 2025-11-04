output "bucket_raw_name" {
  value = aws_s3_bucket.raw.bucket
}

output "bucket_raw_arn" {
  value = aws_s3_bucket.raw.arn
}

output "bucket_transformed_name" {
  value = aws_s3_bucket.transformed.bucket
}

output "bucket_athena_name" {
  value = aws_s3_bucket.athena.bucket
}