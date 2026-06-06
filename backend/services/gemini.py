import json
import re
import base64
from google import genai
from config import GEMINI_API_KEYS

# Try each API key in order until one works
_clients = [genai.Client(api_key=key) for key in GEMINI_API_KEYS]
MODEL = "gemini-2.5-flash"


def _call_gemini(contents) -> str:
    """Call Gemini with fallback: tries each API key until one succeeds."""
    last_error = None
    for i, client in enumerate(_clients):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=contents
            )
            return response.text
        except Exception as e:
            last_error = e
            key_label = "primary" if i == 0 else f"fallback #{i}"
            print(f"Gemini {key_label} key failed: {e}")
            continue
    raise last_error or RuntimeError("All Gemini API keys exhausted")


def _clean_json(text: str) -> str:
    """Strip markdown fences and extract JSON array from Gemini response."""
    text = text.strip()
    # Remove markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Find JSON array boundaries
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text


def extract_from_pdf(pdf_bytes: bytes, prompt: str) -> list[dict]:
    """Send a PDF to Gemini and get back a list of transaction dicts."""
    encoded = base64.b64encode(pdf_bytes).decode("utf-8")
    text = _call_gemini([
        {"mime_type": "application/pdf", "data": encoded},
        prompt
    ])
    return _parse_response(text)


def extract_from_text(text_content: str, prompt: str) -> list[dict]:
    """Send CSV/Excel text content to Gemini and get back a list of transaction dicts."""
    full_prompt = f"{prompt}\n\nHere is the data:\n\n{text_content}"
    text = _call_gemini(full_prompt)
    return _parse_response(text)


def _parse_response(text: str) -> list[dict]:
    """Parse Gemini's text response into a list of dicts."""
    cleaned = _clean_json(text)
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        # Sometimes Gemini returns an object with a key
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    return v
            return [data]
    except json.JSONDecodeError:
        raise ValueError(f"Gemini did not return valid JSON. Raw: {text[:500]}")
    return []
