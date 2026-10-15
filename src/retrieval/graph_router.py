import logging
from typing import List, Dict, Set
from src.schemas.document_tree import DocumentNode

logger = logging.getLogger(__name__)


class GraphRouter:
    """Handles cross-reference graph traversal and cycle detection during pointer expansion."""

    def __init__(self, fetch_node_func):
        self.fetch_node = fetch_node_func

    def expand_pointers_with_cycle_detection(
        self, document_id: str, initial_nodes: List[DocumentNode], max_depth: int = 3
    ) -> List[DocumentNode]:
        hydrated_nodes: Dict[str, DocumentNode] = {node.node_id: node for node in initial_nodes}
        visited_nodes: Set[str] = set(hydrated_nodes.keys())
        queue: List[tuple[str, int]] = []

        for node in initial_nodes:
            for ref_id in node.referenced_nodes:
                queue.append((ref_id, 1))

        while queue:
            target_node_id, depth = queue.pop(0)

            if depth > max_depth or target_node_id in visited_nodes:
                continue

            visited_nodes.add(target_node_id)
            fetched_node = self.fetch_node(document_id, target_node_id)

            if fetched_node:
                hydrated_nodes[target_node_id] = fetched_node
                for next_ref_id in fetched_node.referenced_nodes:
                    if next_ref_id not in visited_nodes:
                        queue.append((next_ref_id, depth + 1))

        return list(hydrated_nodes.values())