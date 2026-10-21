import boto3
from typing import Optional
from src.schemas.document_tree import DocumentNode

class DynamoDBNodeFetcher:
    """Production fetcher retrieving key-value document nodes directly from AWS DynamoDB."""
    def __init__(self, table_name: str = "DocumentTreeStore", region_name: str = "us-east-1"):
        self.dynamodb = boto3.resource("dynamodb", region_name=region_name)
        self.table = self.dynamodb.Table(table_name)

    def get_node(self, document_id: str, node_id: str) -> Optional[DocumentNode]:
        try:
            response = self.table.get_item(
                Key={
                    "PK": f"DOC#{document_id}",
                    "SK": f"NODE#{node_id}"
                }
            )
            item = response.get("Item")
            if not item:
                return None
            return DocumentNode(
                document_id=item["document_id"],
                node_id=item["node_id"],
                title=item["title"],
                content=item["content"],
                parent_rule=item.get("parent_rule"),
                referenced_nodes=item.get("referenced_nodes", []),
                sub_clause_matrix=item.get("sub_clause_matrix", [])
            )
        except Exception as e:
            print(f"Error fetching node {node_id} from DynamoDB: {e}")
            return None
