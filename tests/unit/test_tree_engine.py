from src.schemas.document_tree import DocumentNode
from src.retrieval.graph_router import GraphRouter


def mock_fetch(doc_id: str, node_id: str):
    nodes = {
        "section_4.2": DocumentNode(
            document_id=doc_id,
            node_id="section_4.2",
            title="Hardware Allowance",
            content="See Section 8.1 for foreign vendors.",
            referenced_nodes=["section_8.1"]
        ),
        "section_8.1": DocumentNode(
            document_id=doc_id,
            node_id="section_8.1",
            title="Foreign Supplier Tax",
            content="Requires Form INT-104. Refer to Section 4.2.",
            referenced_nodes=["section_4.2"]  # Cyclical reference test
        )
    }
    return nodes.get(node_id)


def test_cycle_protected_pointer_expansion():
    router = GraphRouter(fetch_node_func=mock_fetch)
    initial = mock_fetch("doc_policy_2026", "section_4.2")
    expanded = router.expand_pointers_with_cycle_detection("doc_policy_2026", [initial])
    
    assert len(expanded) == 2
    assert {"section_4.2", "section_8.1"} == {n.node_id for n in expanded}