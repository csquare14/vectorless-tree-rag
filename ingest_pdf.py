import json
import os
import sys
import ssl
import time
import urllib.request
import urllib.error
import certifi
import boto3
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts raw text from a local PDF file."""
    reader = PdfReader(pdf_path)
    full_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            full_text.append(f"--- PAGE {i+1} ---\n{text}")
    return "\n".join(full_text)

def parse_pdf_to_nodes(document_id: str, raw_text: str, max_retries: int = 3) -> list:
    """Uses Gemini to parse PDF text into structured DocumentNode objects with model fallback handling."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    models = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
    system_instruction = (
        "You are an expert document structural engineer. Convert the raw document text into "
        "a graph structure of interconnected nodes for a vectorless tree retrieval engine.\n\n"
        "OUTPUT REQUIREMENT:\n"
        "Return ONLY a valid JSON array of objects with the following schema:\n"
        "[\n"
        "  {\n"
        "    'document_id': 'string',\n"
        "    'node_id': 'string (e.g., section_1.0, clause_2.1)',\n"
        "    'title': 'string',\n"
        "    'parent_rule': 'string or null',\n"
        "    'content': 'string (body text of this section)',\n"
        "    'referenced_nodes': ['list of other section/node IDs explicitly cross-referenced'],\n"
        "    'sub_clause_matrix': [{'role': '...', 'limit': '...'}] (or empty list)\n"
        "  }\n"
        "]"
    )

    prompt = f"DOCUMENT_ID: {document_id}\n\nRAW TEXT:\n{raw_text}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {
            "temperature": 0.0,
            "responseMimeType": "application/json"
        }
    }

    data = json.dumps(payload).encode("utf-8")
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    last_error = None

    print("🤖 Processing PDF layout with Gemini Ingestion Agent...")
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

        for attempt in range(1, max_retries + 1):
            try:
                with urllib.request.urlopen(req, context=ssl_context) as response:
                    res_body = json.loads(response.read().decode("utf-8"))
                    raw_json_str = res_body["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(raw_json_str)
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode("utf-8")
                last_error = f"Gemini API Error ({e.code}) on {model_name}: {err_msg}"
                if e.code in (503, 429):
                    print(f" Retry {attempt}/{max_retries} on {model_name} (503/429 spike)...")
                    time.sleep(2.0 * attempt)
                    continue
                raise RuntimeError(last_error)
            except Exception as ex:
                last_error = str(ex)
                time.sleep(2.0 * attempt)
                continue

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

def upload_nodes_to_dynamodb(nodes: list, table_name: str = "DocumentTreeStore"):
    """Writes extracted DocumentNodes directly to AWS DynamoDB."""
    resource = boto3.resource("dynamodb", region_name="us-east-1")
    table = resource.Table(table_name)

    print(f" Uploading {len(nodes)} graph nodes to AWS DynamoDB...")
    with table.batch_writer() as batch:
        for node in nodes:
            item = {
                "PK": f"DOC#{node['document_id']}",
                "SK": f"NODE#{node['node_id']}",
                "document_id": node["document_id"],
                "node_id": node["node_id"],
                "title": node.get("title", ""),
                "content": node.get("content", ""),
                "referenced_nodes": node.get("referenced_nodes", []),
                "sub_clause_matrix": node.get("sub_clause_matrix", [])
            }
            if node.get("parent_rule"):
                item["parent_rule"] = node["parent_rule"]
            batch.put_item(Item=item)
    print(" Ingestion Complete! Your PDF graph is live on AWS DynamoDB.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python ingest_pdf.py <document_id> <path_to_pdf>")
        print("Example: python ingest_pdf.py hr_policy_2026 my_policy.pdf")
        sys.exit(1)

    doc_id = sys.argv[1]
    pdf_path = sys.argv[2]

    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        sys.exit(1)

    print(f"\n📄 Reading PDF: {pdf_path}")
    raw_text = extract_text_from_pdf(pdf_path)
    
    nodes = parse_pdf_to_nodes(doc_id, raw_text)
    upload_nodes_to_dynamodb(nodes)

if __name__ == "__main__":
    main()
