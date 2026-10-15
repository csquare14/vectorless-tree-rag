from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("vectorless_tree_rag")


def trace_node_hop(node_id: str, hop_type: str):
    """Tracks tree node navigation hops and retrieval spans via OpenTelemetry."""
    with tracer.start_as_current_span("node_traversal") as span:
        span.set_attribute("tree.node_id", node_id)
        span.set_attribute("tree.hop_type", hop_type)
