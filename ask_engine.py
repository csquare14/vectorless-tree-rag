import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.handlers.query_handler import lambda_handler
from src.retrieval.dynamodb_fetcher import DynamoDBNodeFetcher

def run():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "I am a UX Designer. Can I buy an $1,800 laptop from Germany?"

    print("\n" + "=" * 70)
    print(f"USER QUERY: {query}")
    print("=" * 70)

    # Live AWS DynamoDB fetcher
    aws_fetcher = DynamoDBNodeFetcher()

    event = {"query": query}
    response = lambda_handler(event, None, fetch_node_func=aws_fetcher)

    body = json.loads(response["body"])

    if response.get("statusCode") != 200:
        print("\n Error Execution Failed:")
        print(body.get("error"))
        return

    print("\n--- SYSTEM RESPONSE ---")
    print(body["answer"])
    print("\n" + "-" * 70)
    print(f"CITATIONS USED : {body['citations']}")
    print(f"NODES HYDRATED : {body['nodes_hydrated']}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    run()
