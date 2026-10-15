import os
import json
import boto3
from src.ingestion.tree_builder import TreeBuilder

dynamodb = boto3.resource("dynamodb")
table_name = os.getenv("DYNAMODB_TABLE", "VectorlessRAG_Nodes")
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    """Triggered by S3 PDF uploads to construct tree nodes and persist into DynamoDB."""
    builder = TreeBuilder()

    for record in event.get("Records", []):
        file_key = record["s3"]["object"]["key"]
        doc_id = file_key.split(".")[0]

        mock_raw_sections = [
            {
                "node_id": "section_4.2",
                "parent_node_id": "section_4",
                "title": "Hardware Allowance & Approvals",
                "parent_rule": "All purchases over $50 require manager approval.",
                "content": "UX Designer allowance is $2,000. For foreign suppliers, see Section 8.1.",
                "sub_clause_matrix": [
                    {"role": "UX Designer", "max_allowance": "$2,000", "exception_approver": "Design Director"}
                ],
                "required_roles": ["EMPLOYEE"]
            },
            {
                "node_id": "section_8.1",
                "parent_node_id": "section_8",
                "title": "Foreign Supplier Tax & Import Compliance",
                "content": "Equipment ordered from foreign vendors requires customs filing Form INT-104 prior to payment.",
                "sub_clause_matrix": [],
                "required_roles": ["FINANCE", "EMPLOYEE"]
            }
        ]

        nodes = builder.build_tree_nodes(document_id=doc_id, raw_sections=mock_raw_sections)

        with table.batch_writer() as batch:
            for node in nodes:
                item = node.model_dump()
                item["PK"] = f"DOC#{node.document_id}"
                item["SK"] = f"NODE#{node.node_id}"
                batch.put_item(Item=item)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Successfully ingested PDF tree nodes into DynamoDB"})
    }
