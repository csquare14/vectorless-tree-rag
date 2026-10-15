from pydantic import BaseModel, Field


class EvaluationMetrics(BaseModel):
    """Schema tracking RAG evaluation metrics."""
    context_precision: float = Field(..., description="Ratio of relevant nodes to total hydrated nodes")
    context_recall: float = Field(..., description="Ratio of expected ground-truth nodes retrieved")
    context_sufficiency: float = Field(..., description="Boolean 1.0 or 0.0 indicating complete answer context")
