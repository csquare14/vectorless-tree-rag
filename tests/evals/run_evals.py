import sys
from pathlib import Path

# Add project root directory to sys.path so 'src' imports resolve natively
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json
from src.retrieval.graph_router import GraphRouter
from src.schemas.document_tree import DocumentNode


def mock_fetch(doc_id: str, node_id: str):
    db = {
        "section_4.2": DocumentNode(
            document_id=doc_id, node_id="section_4.2", title="Hardware Allowance",
            content="UX Designer allowance is $2,000. See Section 8.1.",
            referenced_nodes=["section_8.1"]
        ),
        "section_8.1": DocumentNode(
            document_id=doc_id, node_id="section_8.1", title="Foreign Compliance",
            content="Form INT-104 required for German suppliers.",
            referenced_nodes=[]
        )
    }
    return db.get(node_id)


def run_benchmark():
    router = GraphRouter(fetch_node_func=mock_fetch)
    with open("tests/evals/benchmark_dataset.json") as f:
        benchmarks = json.load(f)

    for bench in benchmarks:
        initial = mock_fetch(bench["document_id"], "section_4.2")
        results = router.expand_pointers_with_cycle_detection(bench["document_id"], [initial])
        retrieved_ids = {n.node_id for n in results}
        expected_ids = set(bench["expected_node_ids"])

        recall = len(retrieved_ids.intersection(expected_ids)) / len(expected_ids)
        print(f"Query: {bench['query'][:50]}... | Context Recall: {recall * 100}%")
        assert recall == 1.0, "Context recall benchmark failed!"


if __name__ == "__main__":
    run_benchmark()
