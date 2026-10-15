resource "aws_dynamodb_table" "vectorless_rag_nodes" {
  name         = "VectorlessRAG_Nodes"
  billing_mode = "PAY_PER_REQUEST"
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

  tags = {
    Environment = var.environment
    Project     = "vectorless-tree-rag"
  }
}
