import json
import base64
from pathlib import Path
from typing import Optional
from config import settings
from services.recommendation_service import home_fallback, party_fallback, jewelry_fallback

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

_client = None

def get_client():
    global _client
    if _client is None and settings.GEMINI_API_KEY and genai:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client

def clean_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text[:-3]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Gemini did not return JSON")
    return json.loads(text[start:end+1])

def prompt_for(planner: str, data: dict) -> str:
    base = f"""You are PocketSmart AI, a budget planning assistant.\nPlanner: {planner}\nUser input: {json.dumps(data, ensure_ascii=False)}\n\nReturn ONLY valid JSON with this exact shape:\n{{\"planner\": \"{planner}\", \"budget\": number, \"summary\": string, \"budget_allocation\": object, \"recommendations\": [{{\"category\": string, \"item\": string, \"estimated_price\": number, \"platform\": string, \"search_query\": string, \"reason\": string}}]}}\n\nRules: keep the total estimated spend within the user's budget; never claim live stock or an exact current price; use reasonable estimated prices in INR; platform names should be among Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO when relevant; give 4-8 useful recommendations."""
    if planner == "home":
        base += " Focus on room-by-room furniture, lighting, fans, storage and decor."
    elif planner == "party":
        base += " Allocate budget across food, venue, decoration and entertainment. Consider guest count and event type."
    else:
        base += " Consider occasion, style and optional outfit-image observations. Avoid making claims about identity or body measurements."
    return base

def normalize_links(result: dict):
    from services.recommendation_service import platform_link
    for item in result.get("recommendations", []):
        if not item.get("platform"):
            item["platform"] = "Amazon"
        item["link"] = platform_link(item["platform"], item.get("search_query") or item.get("item", ""))
        item.pop("search_query", None)
    return result

def generate_recommendations(planner: str, data: dict, image_path: Optional[str] = None, image_mime_type: Optional[str] = None) -> dict:
    fallback = {"home": home_fallback, "party": party_fallback, "jewelry": jewelry_fallback}[planner](data)
    client = get_client()
    if not client:
        return fallback
    try:
        contents = [prompt_for(planner, data)]
        if image_path and types:
            image_bytes = Path(image_path).read_bytes()
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime_type or "image/jpeg"))
        response = client.models.generate_content(model=settings.GEMINI_MODEL, contents=contents)
        result = clean_json(response.text)
        if not isinstance(result.get("recommendations"), list) or not result["recommendations"]:
            return fallback
        return normalize_links(result)
    except Exception:
        return fallback
