import json
import os
import sys
import ssl
import time
from pathlib import Path
import urllib.request
import urllib.error
import certifi

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.retrieval.tree_engine import VectorlessTreeEngine


def call_gemini_api(prompt: str, system_instruction: str, json_mode: bool = False, max_retries: int = 3) -> str:
    """Direct REST call to Google AI Studio Free Tier API with model fallbacks on 503/429 errors."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    models = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {"temperature": 0.0}
    }

    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    data = json.dumps(payload).encode("utf-8")
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    last_error = None

    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        for attempt in range(1, max_retries + 1):
            try:
                with urllib.request.urlopen(req, context=ssl_context) as response:
                    res_body = json.loads(response.read().decode("utf-8"))
                    return res_body["candidates"][0]["content"]["parts"][0]["text"]
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode("utf-8")
                last_error = f"Gemini API Error ({e.code}) on {model_name}: {err_msg}"
                if e.code in (503, 429):
                    time.sleep(1.5 * attempt)
                    continue
                raise RuntimeError(last_error)
            except Exception as ex:
                last_error = str(ex)
                time.sleep(1.5 * attempt)
                continue

    raise RuntimeError(last_error)


def classify_intent_and_extract_keys(user_query: str) -> dict:
    router_prompt = (
        "You are an intent-routing agent for an enterprise document tree system.\n"
        "Your task is to analyze the user's plain English query and identify the "
        "target document_id and primary starting node_id.\n\n"
        "Available Document Index:\n"
        "- document_id: 'handbook_v2026'\n"
        "  - section_4.2: Hardware Allowance, Role Spending Limits, Equipment Approvals.\n"
        "  - section_8.1: Foreign Vendor Tax, Customs Clearance, International Suppliers.\n\n"
        "Return ONLY a JSON object with keys: 'document_id' and 'target_node_ids' (a list of string IDs)."
    )

    response_text = call_gemini_api(
        prompt=user_query,
        system_instruction=router_prompt,
        json_mode=True
    )

    return json.loads(response_text)


def evaluate_and_synthesize(user_query: str, assembled_context: str) -> str:
    evaluator_prompt = (
        "You are an authoritative enterprise policy compliance assistant.\n"
        "Your job is to evaluate the user's request against the provided document context.\n\n"
        "RULES FOR YOUR RESPONSE:\n"
        "1. State clearly at the top in bold whether the user CAN or CANNOT proceed.\n"
        "2. Break down the decision into numbered points evaluating every condition found in the context:\n"
        "   - Budget / Role Allowance Limits vs. Requested Amount.\n"
        "   - Mandatory Approval Requirements.\n"
        "   - Foreign/International Compliance & Required Form Numbers.\n"
        "3. Use ONLY facts present in the context. Do not invent policies."
    )

    user_prompt = f"DOCUMENT CONTEXT:\n{assembled_context}\n\nUSER REQUEST:\n{user_query}"

    return call_gemini_api(
        prompt=user_prompt,
        system_instruction=evaluator_prompt,
        json_mode=False
    )


def lambda_handler(event, context, fetch_node_func=None):
    body = event if isinstance(event, dict) else json.loads(event.get("body", "{}"))
    user_query = body.get("query")

    if not user_query:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing 'query' string in request."})}

    try:
        routing = classify_intent_and_extract_keys(user_query)
        doc_id = routing.get("document_id", "handbook_v2026")
        starting_nodes = routing.get("target_node_ids", ["section_4.2"])

        # Instantiated using 'fetcher=' parameter matching VectorlessTreeEngine.__init__ signature
        engine = VectorlessTreeEngine(fetcher=fetch_node_func)
        retrieval_result = engine.retrieve_context(
            document_id=doc_id,
            primary_node_ids=starting_nodes
        )

        assembled_context = retrieval_result["assembled_context"]
        final_answer = evaluate_and_synthesize(user_query, assembled_context)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "answer": final_answer,
                "citations": retrieval_result["citations"],
                "nodes_hydrated": retrieval_result["node_count"]
            }, indent=2)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
