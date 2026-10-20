import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.handlers.query_handler import lambda_handler
from src.schemas.document_tree import DocumentNode


class MockDynamoDBFetcher:
    """Mock node fetcher class that provides the .get_node() method required by VectorlessTreeEngine."""
    
    def get_node(self, document_id: str, node_id: str):
        nodes = {
            "section_4.2": DocumentNode(
                document_id=document_id,
                node_id="section_4.2",
                title="Hardware Allowance & Approvals Matrix",
                parent_rule="All purchases over $50 require mandatory direct manager approval prior to submitting an expense report.",
                content="UX Designer maximum hardware allowance is $2,000. For foreign suppliers outside North America, see Section 8.1.",
                referenced_nodes=["section_8.1"],
                sub_clause_matrix=[
                    {"role": "UX Designer", "max_allowance": "$2,000", "exception_approver": "Design Director"}
                ]
            ),
            "section_8.1": DocumentNode(
                document_id=document_id,
                node_id="section_8.1",
                title="Foreign Supplier Tax & Import Compliance",
                content="Equipment ordered from foreign vendors requires mandatory customs clearance filing Form INT-104 prior to issuing payment.",
                referenced_nodes=[]
            )
        }
        return nodes.get(node_id)


def run():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "I am a UX Designer. Can I buy an $1,800 laptop from Germany?"

    print("\n" + "=" * 70)
    print(f"USER QUERY: {query}")
    print("=" * 70)

    # Instantiate mock fetcher object
    mock_fetcher = MockDynamoDBFetcher()

    event = {"query": query}
    response = lambda_handler(event, None, fetch_node_func=mock_fetcher)
    
    body = json.loads(response["body"])

    if response.get("statusCode") != 200:
        print("\n❌ Error Execution Failed:")
        print(body.get("error"))
        return

    print("\n--- SYSTEM RESPONSE ---")
    print(body["answer"])
    print("\n" + "-" * 70)
    print(f"CITATIONS USED  : {body['citations']}")
    print(f"NODES HYDRATED  : {body['nodes_hydrated']}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run()
