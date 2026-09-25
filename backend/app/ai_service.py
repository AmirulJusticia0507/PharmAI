import httpx
import base64
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-4o-mini")


async def chat_completion(messages: list[dict], model: str | None = None) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "PharmAI",
            },
            json={"model": model or AI_MODEL, "messages": messages, "max_tokens": 1024},
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
                        "Analisis foto obat atau kemasannya, termasuk tablet, kaplet, kapsul, cairan, "
                        "sirup, suspensi, tetes, salep, krim, gel, inhaler, injeksi, suppositoria, atau "
                        "patch. Kembalikan JSON: "
                        '{"name": "nama obat", "dosage": "dosis", "dosage_form": "bentuk sediaan", '
                        '"category": "kategori dalam Bahasa Indonesia", '
                        '"active_ingredients": ["nama zat aktif"], '
                        '"registration_number": "nomor yang terlihat pada kemasan atau kosong", '
                        '"description": "deskripsi singkat dalam Bahasa Indonesia", '
                        '"confidence": 0.0-1.0}. '
                        "Pertahankan nama obat, dosis, dan zat aktif sebagaimana tertulis. Jangan "
                        "mengarang kandungan atau nomor izin edar. Jika tidak terlihat jelas, gunakan "
                        "nilai kosong dan confidence rendah. Utamakan tulisan pada kemasan; jangan "
                        "mengenali obat cair atau topikal hanya dari warna dan bentuk wadah. Hanya "
                        "kembalikan JSON valid."
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
            "name": "Tidak teridentifikasi",
            "dosage": "",
            "dosage_form": "",
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
                        "Baca dan transkripsikan resep dokter ini. Kembalikan JSON: "
                        '{"patient_name": "", "doctor_name": "", '
                        '"medications": [{"name": "", "dosage": "", "frequency": "", "duration": ""}], '
                        '"notes": ""}. '
                        "Pertahankan nama pasien, dokter, obat, dosis, dan teks asli yang terbaca. "
                        "Tulis frequency, duration, dan notes dalam Bahasa Indonesia. Jangan menebak "
                        "tulisan yang tidak terbaca; gunakan nilai kosong. Hanya kembalikan JSON valid."
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
                "Anda adalah pakar farmasi. Analisis interaksi obat. Seluruh penjelasan, "
                "rekomendasi, dan ringkasan wajib menggunakan Bahasa Indonesia yang mudah "
                "dipahami. Selalu kembalikan JSON valid."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Periksa interaksi antara obat berikut: {drugs_str}. "
                "Kembalikan JSON: "
                '{"interactions": [{"drugs": ["A", "B"], "severity": "high/medium/low", '
                '"description": "penjelasan dalam Bahasa Indonesia", '
                '"recommendation": "tindakan yang disarankan dalam Bahasa Indonesia"}], '
                '"overall_safety": "safe/caution/unsafe", '
                '"summary": "ringkasan singkat dalam Bahasa Indonesia"}. '
                "Jangan terjemahkan nama obat atau nilai severity dan overall_safety."
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


async def analyze_drug(drug_data: dict) -> dict:
    name = drug_data.get("name") or ""
    generic_name = drug_data.get("generic_name") or ""
    category = drug_data.get("category") or ""
    description = drug_data.get("description") or ""
    dosage_form = drug_data.get("dosage_form") or ""
    manufacturer = drug_data.get("manufacturer") or ""
    indication = drug_data.get("indication") or ""
    benefit = drug_data.get("benefit") or ""
    dosage = drug_data.get("dosage") or ""
    usage_time = drug_data.get("usage_time") or []
    frequency = drug_data.get("frequency") or ""
    active_ingredients = drug_data.get("active_ingredients") or []

    has_existing_data = any([indication, benefit, dosage, usage_time, frequency])

    if has_existing_data:
        prompt = (
            f"Berikut adalah data obat yang sudah ada:\n"
            f"Nama: {name}\n"
            f"Nama generik: {generic_name}\n"
            f"Kategori: {category}\n"
            f"Bentuk sediaan: {dosage_form}\n"
            f"PRODUSEN: {manufacturer}\n"
            f"Deskripsi: {description}\n"
            f"Zat aktif: {', '.join(active_ingredients) if active_ingredients else 'N/A'}\n"
            f"Indikasi saat ini: {indication or 'kosong'}\n"
            f"Manfaat saat ini: {benefit or 'kosong'}\n"
            f"Dosis saat ini: {dosage or 'kosong'}\n"
            f"Waktu pakai saat ini: {', '.join(usage_time) if usage_time else 'kosong'}\n"
            f"Frekuensi saat ini: {frequency or 'kosong'}\n\n"
            f"Berdasarkan data di atas, berikan analisis lengkap penggunaan yang aman dan "
            f"sesuai petunjuk. Jika ada field yang kosong, lengkapi berdasarkan pengetahuan "
            f"farmakologi obat tersebut. Jika ada field yang sudah terisi, verifikasi dan "
            f"pertahankan kesesuaiannya. Kembalikan JSON valid:\n"
            f'{{"indication": "untuk apa obat ini digunakan", '
            f'"benefit": "manfaat penggunaan", '
            f'"dosage": "dosis yang disarankan", '
            f'"usage_time": ["pagi", "siang", "sore", "malam"], '
            f'"frequency": "frekuensi penggunaan", '
            f'"confidence": 0.0-1.0}}'
        )
    else:
        prompt = (
            f"Berikan analisis penggunaan yang aman dan sesuai petunjuk untuk obat berikut:\n"
            f"Nama: {name}\n"
            f"Nama generik: {generic_name}\n"
            f"Kategori: {category}\n"
            f"Bentuk sediaan: {dosage_form}\n"
            f"PRODUSEN: {manufacturer}\n"
            f"Deskripsi: {description}\n"
            f"Zat aktif: {', '.join(active_ingredients) if active_ingredients else 'N/A'}\n\n"
            f"Kembalikan JSON valid dengan field:\n"
            f'{{"indication": "untuk apa obat ini digunakan", '
            f'"benefit": "manfaat penggunaan", '
            f'"dosage": "dosis yang disarankan", '
            f'"usage_time": ["pagi", "siang", "sore", "malam"], '
            f'"frequency": "frekuensi penggunaan", '
            f'"confidence": 0.0-1.0}}\n'
            f"Jika informasi tidak cukup, gunakan nilai kosong dan confidence rendah. "
            f"Semua teks dalam Bahasa Indonesia."
        )

    messages = [
        {
            "role": "system",
            "content": (
                "Anda adalah pakar farmasi Indonesia. Berikan analisis penggunaan obat "
                "yang akurat, aman, dan mudah dipahami dalam Bahasa Indonesia. "
                "Selalu kembalikan JSON valid."
            ),
        },
        {"role": "user", "content": prompt},
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
            "indication": "",
            "benefit": "",
            "dosage": "",
            "usage_time": [],
            "frequency": "",
            "confidence": 0.0,
            "raw_response": result,
        }
