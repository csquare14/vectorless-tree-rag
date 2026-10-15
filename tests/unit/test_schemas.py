from src.schemas.document_tree import DocumentNode

def test_document_node_validation():
    sample_data = {
        "document_id": "doc_policy_2026",
        "node_id": "section_4.2",
        "title": "Hardware Allowance",
        "parent_rule": "All purchases over $50 require manager approval.",
        "content": "UX Designer allowance is $2,000. See Section 8.1 for foreign vendors.",
        "sub_clause_matrix": [
            {"role": "UX Designer", "max_allowance": "$2,000"}
        ],
        "referenced_nodes": ["section_8.1"]
    }
    
    node = DocumentNode(**sample_data)
    assert node.node_id == "section_4.2"
    assert node.referenced_nodes == ["section_8.1"]
    assert len(node.sub_clause_matrix) == 1