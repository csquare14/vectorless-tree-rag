import re
from typing import List
from src.schemas.document_tree import PointerLink


class PointerExtractor:
    """Regex and pattern-based engine to extract structural cross-references from section text."""

    def __init__(self):
        self.patterns = [
            r'(?:[Ss]ee|[Rr]efer\s+to)\s+[Ss]ection\s+(\d+(?:\.\d+)*)',
            r'(?:[Ss]ee|[Rr]efer\s+to)\s+[Cc]lause\s+(\d+(?:\.\d+)*)',
            r'[Ss]ection\s+(\d+(?:\.\d+)*)'
        ]

    def extract_pointers(self, source_node_id: str, text: str) -> List[PointerLink]:
        pointers: List[PointerLink] = []
        seen_targets = set()

        for pattern in self.patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                sec_num = match.group(1)
                target_node_id = f"section_{sec_num}"
                
                # Prevent self-references and duplicate pointers within the same node
                if target_node_id != source_node_id and target_node_id not in seen_targets:
                    seen_targets.add(target_node_id)
                    pointers.append(
                        PointerLink(
                            source_node_id=source_node_id,
                            target_node_id=target_node_id,
                            citation_text=match.group(0)
                        )
                    )
        return pointers