import json
from src.retrieval.tree_engine import VectorlessTreeEngine


def lambda_handler(event, context):
    """Executes vectorless retrieval & dynamic pointer hydration for incoming user queries."""
    body = event if isinstance(event, dict) else json.loads(event.get("body", "{}"))
    
    document_id = body.get("document_id")
    target_nodes = body.get("target_node_ids", ["section_4.2"])
    
    if not document_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing 'document_id'"})}

    engine = VectorlessTreeEngine()
    retrieval_result = engine.retrieve_context(
        document_id=document_id,
        primary_node_ids=target_nodes
    )

    return {
        "statusCode": 200,
        "body": json.dumps(retrieval_result)
    }
