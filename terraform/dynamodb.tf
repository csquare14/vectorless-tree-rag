terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

# DynamoDB Single-Table for Vectorless Tree-RAG
resource "aws_dynamodb_table" "document_tree_store" {
  name         = "DocumentTreeStore"
  billing_mode = "PAY_PER_REQUEST" # On-demand capacity for auto-scaling
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "DocumentTreeStore"
    Environment = "production"
    Project     = "vectorless-tree-rag"
  }
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.document_tree_store.name
  description = "The name of the DynamoDB table."
}

output "dynamodb_table_arn" {
  value       = aws_dynamodb_table.document_tree_store.arn
  description = "The ARN of the DynamoDB table."
}
