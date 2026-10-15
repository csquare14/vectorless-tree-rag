import os
import boto3
from typing import Optional
from src.schemas.document_tree import DocumentNode


class DynamoDBNodeFetcher:
    """Tool for direct Key-Value lookups on DynamoDB node tables."""

    def __init__(self, table_name: Optional[str] = None):
        self.table_name = table_name or os.getenv("DYNAMODB_TABLE", "VectorlessRAG_Nodes")
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)

    def get_node(self, document_id: str, node_id: str) -> Optional[DocumentNode]:
        response = self.table.get_item(
            Key={
                "PK": f"DOC#{document_id}",
                "SK": f"NODE#{node_id}"
            }
        )
        item = response.get("Item")
        if not item:
            return None

        return DocumentNode(**item)