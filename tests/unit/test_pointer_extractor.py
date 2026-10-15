from src.ingestion.pointer_extractor import PointerExtractor

def test_pointer_extraction():
    extractor = PointerExtractor()
    text = "For UX Designer allowances, see Section 8.1. Refer to Section 4.2 for general policies."
    pointers = extractor.extract_pointers("section_4.0", text)
    
    target_ids = [p.target_node_id for p in pointers]
    assert "section_8.1" in target_ids
    assert "section_4.2" in target_ids