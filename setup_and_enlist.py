import os

# 1. Update tests/evals/run_evals.py with sys.path root resolution
run_evals_code = """import sys
from pathlib import Path

# Set project root in sys.path to allow standalone execution
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
"""

with open("tests/evals/run_evals.py", "w") as f:
    f.write(run_evals_code.strip() + "\n")

# 2. Create run_all.py runner at root
run_all_code = """import subprocess
import sys

def run_suite():
    print("==================================================")
    print("1. RUNNING PYTEST UNIT SUITE (PHASES 1 - 4)")
    print("==================================================")
    pytest_res = subprocess.run([sys.executable, "-m", "pytest"])
    if pytest_res.returncode != 0:
        print("\\n❌ Pytest failed!")
        sys.exit(1)

    print("\\n==================================================")
    print("2. RUNNING VECTORLESS RAG EVALUATION BENCHMARKS (PHASE 5)")
    print("==================================================")
    eval_res = subprocess.run([sys.executable, "tests/evals/run_evals.py"])
    if eval_res.returncode != 0:
        print("\\n❌ Benchmark Evaluations failed!")
        sys.exit(1)

    print("\\n==================================================")
    print("✅ ALL TESTS & BENCHMARK EVALUATIONS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_suite()
"""

with open("run_all.py", "w") as f:
    f.write(run_all_code.strip() + "\n")

print("Updated run_evals.py and created run_all.py successfully!")
