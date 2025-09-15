output "bucket_id" {
  description = "ID of the S3 bucket"
  value       = aws_s3_bucket.submissions.id
}
