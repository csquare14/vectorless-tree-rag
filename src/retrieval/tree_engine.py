import json
from typing import List, Dict, Any, Optional
from src.schemas.document_tree import DocumentNode
from src.retrieval.graph_router import GraphRouter
from src.agents.tools.fetch_node_tool import DynamoDBNodeFetcher


class VectorlessTreeEngine:
    """Main retrieval engine: target fetch + recursive pointer hydration."""

    def __init__(self, fetcher: Optional[DynamoDBNodeFetcher] = None):
        self.fetcher = fetcher or DynamoDBNodeFetcher()
        self.graph_router = GraphRouter(fetch_node_func=self.fetcher.get_node)

    def retrieve_context(self, document_id: str, primary_node_ids: List[str]) -> Dict[str, Any]:
        initial_nodes: List[DocumentNode] = []
        for node_id in primary_node_ids:
            node = self.fetcher.get_node(document_id, node_id)
            if node:
                initial_nodes.append(node)

        hydrated_nodes = self.graph_router.expand_pointers_with_cycle_detection(
            document_id=document_id,
            initial_nodes=initial_nodes
        )

        formatted_context_blocks = []
        citations = []

        for node in hydrated_nodes:
            citations.append(node.node_id)
            block = f"=== SECTION: {node.node_id} | {node.title} ==="
            if node.parent_rule:
                block += f"\n[GOVERNING PARENT RULE]: {node.parent_rule}"
            if node.sub_clause_matrix:
                block += f"\n[TABLE MATRIX]: {json.dumps(node.sub_clause_matrix)}"
            if node.content:
                block += f"\n[CONTENT]: {node.content}"
            formatted_context_blocks.append(block)

        return {
            "assembled_context": "\n\n".join(formatted_context_blocks),
            "citations": citations,
            "node_count": len(hydrated_nodes)
        }