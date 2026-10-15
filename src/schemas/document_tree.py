from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentNode(BaseModel):
    """Represents a single structural node in a hierarchical document tree."""
    document_id: str = Field(..., description="Unique ID of the parent document")
    node_id: str = Field(..., description="Unique section key (e.g., 'section_4.2')")
    parent_node_id: Optional[str] = Field(None, description="Parent section ID for hierarchy navigation")
    title: str = Field(..., description="Section title or heading name")
    parent_rule: Optional[str] = Field(None, description="Governing policy/rule inherited from parent context")
    content: str = Field("", description="Raw textual narrative contained in the section")
    sub_clause_matrix: List[Dict[str, Any]] = Field(default_factory=list, description="Structured tabular data preserved as dictionaries")
    referenced_nodes: List[str] = Field(default_factory=list, description="Explicit cross-reference pointer IDs")
    required_roles: List[str] = Field(default_factory=list, description="RBAC roles authorized to view this node")


class TreeIndex(BaseModel):
    """High-level Table of Contents summary used for LLM tree navigation."""
    document_id: str
    document_name: str
    toc_structure: List[Dict[str, Any]] = Field(..., description="Lightweight tree hierarchy")


class PointerLink(BaseModel):
    """Edge representation between source and target reference nodes."""
    source_node_id: str
    target_node_id: str
    citation_text: str = Field(..., description="Raw string match that triggered the pointer")