import httpx
import base64
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-4o-mini")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openrouter").lower()
GRIPHUB_API_KEY = os.getenv("GRIPHUB_API_KEY", "")
GRIPHUB_BASE_URL = os.getenv("GRIPHUB_BASE_URL", "https://griphubrouter.web.id/v1")
GRIPHUB_MODEL = os.getenv("GRIPHUB_MODEL", "gemini-3.8-flash")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
PREMIUM_IMAGE_MODEL = os.getenv(
    "PREMIUM_IMAGE_MODEL", "@cf/black-forest-labs/flux-1-schnell"
)
STANDARD_IMAGE_MODEL = os.getenv(
    "STANDARD_IMAGE_MODEL", "@cf/black-forest-labs/flux-1-schnell"
)


async def chat_completion(messages: list[dict], model: str | None = None) -> str:
    if AI_PROVIDER == "griphub":
        if not GRIPHUB_API_KEY:
            raise ValueError("GRIPHUB_API_KEY belum dikonfigurasi")
        base_url = GRIPHUB_BASE_URL
        api_key = GRIPHUB_API_KEY
        selected_model = model or GRIPHUB_MODEL
    else:
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY belum dikonfigurasi")
        base_url = OPENROUTER_BASE_URL
        api_key = OPENROUTER_API_KEY
        selected_model = model or AI_MODEL

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "PharmAI",
            },
            json={"model": selected_model, "messages": messages, "max_tokens": 2048},
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


async def assess_symptoms(data: dict) -> dict:
    prompt = f"""Pengguna menceritakan keluhan kesehatan berikut.
Keluhan: {data.get('complaint', '')}
Usia: {data.get('age') or 'tidak disebutkan'}
Jenis kelamin: {data.get('sex') or 'tidak disebutkan'}
Durasi: {data.get('duration') or 'tidak disebutkan'}
Kondisi/penyakit lain: {data.get('existing_conditions') or 'tidak ada/tidak disebutkan'}
Obat yang sedang digunakan: {data.get('current_medicines') or 'tidak ada/tidak disebutkan'}
Alergi: {data.get('allergies') or 'tidak ada/tidak disebutkan'}
Kehamilan/menyusui: {data.get('pregnancy_status') or 'tidak relevan/tidak disebutkan'}

Lakukan triase konservatif. Jangan mendiagnosis, meresepkan, atau menyarankan antibiotik,
obat keras, penghentian obat dokter, maupun dosis personal. Bila informasi penting kurang,
nyatakan keterbatasannya. Opsi obat hanya boleh obat bebas untuk keluhan ringan, dengan
peringatan kontraindikasi dan anjuran konfirmasi apoteker. Jika ada tanda bahaya, prioritaskan
pertolongan medis dan jangan menunda dengan swamedikasi.

Kembalikan JSON valid saja:
{{"urgency":"emergency/urgent/routine/self_care", "assessment":"ringkasan non-diagnostik",
"self_care":["langkah non-obat"], "otc_options":[{{"medicine":"nama generik/golongan",
"purpose":"kegunaan", "directions":"ikuti label/aturan umum non-personal",
"cautions":"kontraindikasi dan perhatian"}}], "red_flags":["tanda bahaya yang relevan"],
"next_steps":["langkah berikutnya"], "disclaimer":"batasan singkat"}}"""
    result = await chat_completion([
        {"role": "system", "content": (
            "Anda adalah asisten edukasi kesehatan dan farmasi Indonesia yang mengutamakan "
            "keselamatan. Anda bukan dokter, tidak membuat diagnosis, dan selalu memberi JSON valid."
        )},
        {"role": "user", "content": prompt},
    ])
    import json
    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(cleaned)
    except Exception:
        return {
            "urgency": "routine", "assessment": result, "self_care": [],
            "otc_options": [], "red_flags": [],
            "next_steps": ["Konfirmasikan keluhan kepada dokter atau apoteker."],
            "disclaimer": "Hasil AI bukan diagnosis atau resep.",
        }


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


async def generate_drug_visual(drug_data: dict, use_premium: bool = False) -> dict:
    if not GOOGLE_API_KEY and (not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN):
        raise ValueError("Provider generasi gambar belum dikonfigurasi")

    name = drug_data.get("name") or ""
    generic_name = drug_data.get("generic_name") or ""
    dosage_form = drug_data.get("dosage_form") or ""
    manufacturer = drug_data.get("manufacturer") or ""
    description = drug_data.get("description") or ""
    active_ingredients = drug_data.get("active_ingredients") or []
    dosage = drug_data.get("dosage") or ""
    color = drug_data.get("color") or ""
    shape = drug_data.get("shape") or ""
    imprint = drug_data.get("imprint") or ""

    prompt = (
        f"Gambar realistis dari obat atau kemasannya. "
        f"Nama obat: {name}. Nama generik: {generic_name}. "
        f"Bentuk sediaan: {dosage_form}. "
        f"Warna: {color or 'tidak ditentukan'}. "
        f"Bentuk: {shape or 'tidak ditentukan'}. "
        f"Imprint/atau kode pada permukaan: {imprint or 'tidak ada'}. "
        f"Dosis: {dosage or 'tidak ditentukan'}. "
        f"PRODUSEN: {manufacturer or 'tidak ditentukan'}. "
        f"Zat aktif: {', '.join(active_ingredients) if active_ingredients else 'N/A'}. "
        f"Deskripsi: {description or 'tidak tersedia'}. "
        f"Gambarkan permukaan obat (tablet, kapsul, kaplet) secara detail termasuk warna, "
        f"bentuk, tekstur, dan imprint jika ada. Jika obat cair, gambarkan butir/ Botol "
        f"kemasannya. Fotografi realistis dengan pencahayaan studio yang baik, latar belakang "
        f"putih bersih. Jangan termasuk teks, logo, atau watermark."
    )

    gemini_error = None
    if GOOGLE_API_KEY:
        gemini_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{GEMINI_IMAGE_MODEL}:generateContent?key={GOOGLE_API_KEY}"
        )
        try:
            async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
                gemini_resp = await client.post(
                    gemini_url,
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"responseModalities": ["IMAGE"]},
                    },
                )
            if gemini_resp.is_success:
                data = gemini_resp.json()
                parts = ((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
                for part in parts:
                    inline = part.get("inlineData") or part.get("inline_data") or {}
                    if inline.get("data"):
                        mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
                        return {
                            "image_url": f"data:{mime};base64,{inline['data']}",
                            "revised_prompt": prompt,
                            "model": GEMINI_IMAGE_MODEL,
                            "premium": False,
                        }
                gemini_error = "Gemini tidak mengembalikan data gambar"
            else:
                try:
                    message = (gemini_resp.json().get("error") or {}).get("message")
                except (ValueError, AttributeError):
                    message = None
                if gemini_resp.status_code == 429:
                    gemini_error = "Kuota Gemini Flash Image habis atau tidak tersedia pada free tier"
                else:
                    gemini_error = f"Gemini gagal (HTTP {gemini_resp.status_code}){f': {message}' if message else ''}"
        except httpx.TimeoutException:
            gemini_error = "Gemini melewati batas waktu"
        except httpx.RequestError:
            gemini_error = "Gemini tidak dapat dihubungi"

        if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
            raise ValueError(gemini_error)

    model = PREMIUM_IMAGE_MODEL if use_premium else STANDARD_IMAGE_MODEL
    image_api_url = (
        f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}"
        f"/ai/run/{model}"
    )

    try:
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            resp = await client.post(
                image_api_url,
                headers={
                    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json={"prompt": prompt, "steps": 4},
            )
    except httpx.TimeoutException as exc:
        raise ValueError("Generator gambar melewati batas waktu. Silakan coba lagi.") from exc
    except httpx.RequestError as exc:
        raise ValueError("Generator gambar tidak dapat dihubungi. Silakan coba lagi.") from exc

    if not resp.is_success:
        try:
            payload = resp.json()
            errors = payload.get("errors") or []
            message = errors[0].get("message") if errors else None
        except (ValueError, AttributeError, IndexError):
            message = None
        cloudflare_error = (
            f"Provider gambar gagal (HTTP {resp.status_code})"
            f"{f': {message}' if message else ''}"
        )
        raise ValueError(f"{gemini_error}; fallback Cloudflare: {cloudflare_error}" if gemini_error else cloudflare_error)

    try:
        data = resp.json()
        result = data.get("result") or {}
        image_data = result.get("image") if isinstance(result, dict) else ""
    except ValueError:
        image_data = base64.b64encode(resp.content).decode() if resp.content else ""
    if not image_data:
        raise ValueError("Cloudflare Workers AI tidak mengembalikan data gambar")

    image_url = f"data:image/jpeg;base64,{image_data}"

    return {
        "image_url": image_url,
        "revised_prompt": prompt,
        "model": model,
        "premium": use_premium,
    }
