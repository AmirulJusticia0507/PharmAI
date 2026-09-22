import httpx
import base64
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


async def chat_completion(messages: list[dict], model: str = "openai/gpt-3.5-turbo") -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "PharmAI",
            },
            json={"model": model, "messages": messages, "max_tokens": 1024},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def analyze_pill_image(image_bytes: bytes, mime: str = "image/jpeg") -> dict:
    b64 = base64.b64encode(image_bytes).decode()
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Analyze this pill/capsule image. Return JSON with: "
                        '{"name": "drug name", "dosage": "dosage", '
                        '"category": "drug category", '
                        '"active_ingredients": ["ingredient name"], '
                        '"registration_number": "number visible on package or empty", '
                        '"description": "brief description", '
                        '"confidence": 0.0-1.0}. '
                        "Do not invent ingredients or a registration number. If they are not "
                        "clearly visible, return an empty list or empty string. If unsure, set "
                        "confidence low. Only return valid JSON."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"},
                },
            ],
        }
    ]
    result = await chat_completion(messages)
    import json

    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(cleaned)
    except Exception:
        return {
            "name": "Unknown",
            "dosage": "",
            "category": "",
            "active_ingredients": [],
            "registration_number": "",
            "description": result,
            "confidence": 0.0,
        }


async def ocr_prescription(image_bytes: bytes, mime: str = "image/jpeg") -> dict:
    b64 = base64.b64encode(image_bytes).decode()
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Read and transcribe this handwritten doctor prescription. "
                        "Return JSON with: "
                        '{"patient_name": "", "doctor_name": "", '
                        '"medications": [{"name": "", "dosage": "", "frequency": "", "duration": ""}], '
                        '"notes": ""}. '
                        "Only return valid JSON."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"},
                },
            ],
        }
    ]
    result = await chat_completion(messages)
    import json

    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(cleaned)
    except Exception:
        return {"raw_text": result, "medications": []}


async def check_drug_interactions(drug_names: list[str]) -> dict:
    drugs_str = ", ".join(drug_names)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a pharmaceutical expert. Analyze drug interactions. "
                "Always return valid JSON."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Check interactions between these drugs: {drugs_str}. "
                "Return JSON: "
                '{"interactions": [{"drugs": ["A", "B"], "severity": "high/medium/low", '
                '"description": "explanation", "recommendation": "what to do"}], '
                '"overall_safety": "safe/caution/unsafe", '
                '"summary": "brief summary"}.'
            ),
        },
    ]
    result = await chat_completion(messages)
    import json

    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(cleaned)
    except Exception:
        return {"summary": result, "interactions": [], "overall_safety": "unknown"}
