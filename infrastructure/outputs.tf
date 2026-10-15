output "dynamodb_table_name" {
  value       = aws_dynamodb_table.vectorless_rag_nodes.name
  description = "Name of the DynamoDB table"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.raw_pdfs.bucket
  description = "Name of the raw PDF ingestion S3 bucket"
}
