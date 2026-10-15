from typing import List, Dict, Any
from src.schemas.document_tree import DocumentNode
from src.ingestion.pointer_extractor import PointerExtractor


class TreeBuilder:
    """Compiles raw parsed sections into structured, pointer-linked DocumentNode objects."""

    def __init__(self):
        self.extractor = PointerExtractor()

    def build_tree_nodes(self, document_id: str, raw_sections: List[Dict[str, Any]]) -> List[DocumentNode]:
        nodes: List[DocumentNode] = []

        for sec in raw_sections:
            source_id = sec["node_id"]
            content = sec.get("content", "")
            
            # Extract explicit pointers
            extracted_links = self.extractor.extract_pointers(source_id, content)
            ref_nodes = [link.target_node_id for link in extracted_links]

            node = DocumentNode(
                document_id=document_id,
                node_id=source_id,
                parent_node_id=sec.get("parent_node_id"),
                title=sec["title"],
                parent_rule=sec.get("parent_rule"),
                content=content,
                sub_clause_matrix=sec.get("sub_clause_matrix", []),
                referenced_nodes=ref_nodes,
                required_roles=sec.get("required_roles", [])
            )
            nodes.append(node)

        return nodes