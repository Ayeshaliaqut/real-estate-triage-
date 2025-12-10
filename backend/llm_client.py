import os
import json
import logging
from typing import Dict, Any, Optional

import requests

from .constants import LLM_DEFAULT_FALLBACK

LOGGER = logging.getLogger(__name__)

FREE_API_URL = os.getenv("FREE_LLM_API_URL", "").strip()
FREE_API_KEY = os.getenv("FREE_LLM_API_KEY", "").strip()
DEFAULT_TIMEOUT = 10  # seconds


def build_prompt(lead: Dict[str, Any]) -> str:
    """
    Instruct the model to return ONLY JSON with intent_label and short_reason.
    """
    prompt = (
        "You are a JSON-only classifier. Given the lead fields below, return ONLY a JSON "
        "object with two keys:\n"
        "  - intent_label (one of [serious_buyer, serious_renter, seller, casual_inquiry, spam, not_relevant])\n"
        "  - short_reason (a single short sentence explaining the classification)\n"
        "Respond with no extra commentary or explanation—ONLY the JSON.\n\n"
        f"Lead:\n"
        f"name: {lead.get('name')}\n"
        f"property_type: {lead.get('property_type')}\n"
        f"budget: {lead.get('budget')}\n"
        f"location_preference: {lead.get('location_preference')}\n"
        f"timeframe_to_move: {lead.get('timeframe_to_move')}\n"
        f"message: {lead.get('message')}\n"
        f"source: {lead.get('source')}\n\n"
        "Return the JSON now."
    )
    return prompt


def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    #for finding out jason format
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    candidate = text[start:end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Try replacing single quotes with double quotes 
        try:
            alt = candidate.replace("'", '"')
            return json.loads(alt)
        except Exception:
            return None


def build_request_payload(prompt: str) -> Dict[str, Any]:
    """
    Build OpenAI-compatible chat completion payload for Groq API.
    Uses llama-3.3-70b-versatile - a current, supported model.
    """
    return {
        "model": "llama-3.3-70b-versatile",  #current model
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 150,
        "temperature": 0.0
    }


def call_llm_for_intent(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call Groq API for intent classification.
    """
    if not FREE_API_URL or not FREE_API_KEY:
        LOGGER.info("FREE_LLM not configured; returning fallback intent.")
        return LLM_DEFAULT_FALLBACK

    prompt = build_prompt(lead)
    payload = build_request_payload(prompt)
    headers = {
        "Authorization": f"Bearer {FREE_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(FREE_API_URL, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
        
        if resp.status_code != 200:
            LOGGER.error(f"Groq API returned {resp.status_code}: {resp.text}")
        
        resp.raise_for_status()

        data = resp.json()
        if "choices" in data and len(data["choices"]) > 0:
            message_content = data["choices"][0].get("message", {}).get("content", "")
            parsed = _extract_json_from_text(message_content)
            if parsed and "intent_label" in parsed:
                return {
                    "intent_label": parsed.get("intent_label", "casual_inquiry"),
                    "short_reason": parsed.get("short_reason", "")
                }
    except Exception as e:
        LOGGER.error("LLM request failed: %s", e)

    LOGGER.info("Returning LLM fallback intent.")
    return LLM_DEFAULT_FALLBACK