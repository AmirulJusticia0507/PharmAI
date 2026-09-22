"""Import registered medicines from the official BPOM product catalogue."""

import argparse
import html
import re
import time
from datetime import date, datetime, timezone

import httpx
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Drug


BPOM_LIST_URL = "https://cekbpom.pom.go.id/produk-obat"
BPOM_DATA_URL = "https://cekbpom.pom.go.id/produk-dt/01"
BPOM_DETAIL_URL = "https://cekbpom.pom.go.id/produk/{product_id}/{application_id}/detail"
USER_AGENT = "PharmAI/0.1 (BPOM catalogue sync; public registered-product data)"


def clean(value) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(value or "")).replace("<br>", " ")).strip(" -")


def ingredients(value) -> list[str]:
    decoded = html.unescape(str(value or ""))
    return [clean(item) for item in re.split(r"<br\s*/?>|\r?\n", decoded, flags=re.I) if clean(item)]


def parse_date(value):
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except ValueError:
        return None


def fetch_page(client: httpx.Client, token: str, start: int, length: int) -> dict:
    response = client.post(
        BPOM_DATA_URL,
        data={
            "draw": start // length + 1,
            "start": start,
            "length": length,
            "search[value]": "",
            "search[regex]": "false",
        },
        headers={
            "X-CSRF-TOKEN": token,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": BPOM_LIST_URL,
        },
    )
    response.raise_for_status()
    return response.json()


def map_product(row: dict, checked_at: datetime) -> dict:
    product_id = clean(row.get("PRODUCT_ID"))
    application_id = clean(row.get("APPLICATION_ID"))
    status = clean(row.get("STATUS")).lower()
    registration_status = "active" if status == "berlaku" else "unverified"
    brand = clean(row.get("PRODUCT_BRANDS"))
    package = clean(row.get("PRODUCT_PACKAGE"))
    description_parts = [part for part in (f"Merek: {brand}" if brand else "", f"Kemasan: {package}" if package else "") if part]
    return {
        "name": clean(row.get("PRODUCT_NAME")) or "Produk obat BPOM",
        "generic_name": None,
        "category": "Obat BPOM",
        "description": ". ".join(description_parts) or None,
        "dosage_form": clean(row.get("PRODUCT_FORM")) or None,
        "manufacturer": clean(row.get("MANUFACTURER_NAME")) or None,
        "active_ingredients": ingredients(row.get("INGREDIENTS")),
        "registration_number": clean(row.get("PRODUCT_REGISTER")),
        "registration_status": registration_status,
        "registration_expires_at": parse_date(row.get("EXPIRE_DATE")),
        "regulatory_source_url": BPOM_DETAIL_URL.format(product_id=product_id, application_id=application_id),
        "regulatory_checked_at": checked_at,
        "regulatory_notes": f"Status katalog resmi BPOM: {clean(row.get('STATUS')) or 'belum tersedia'}.",
    }


def upsert_batch(rows: list[dict]) -> tuple[int, int]:
    valid = [row for row in rows if row["registration_number"]]
    numbers = [row["registration_number"] for row in valid]
    inserted = updated = 0
    with SessionLocal() as db:
        existing = {
            drug.registration_number: drug
            for drug in db.scalars(select(Drug).where(Drug.registration_number.in_(numbers)))
        }
        for values in valid:
            drug = existing.get(values["registration_number"])
            if drug:
                for key, value in values.items():
                    setattr(drug, key, value)
                updated += 1
            else:
                db.add(Drug(**values))
                inserted += 1
        db.commit()
    return inserted, updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Sinkronisasi produk obat resmi BPOM ke PharmAI")
    parser.add_argument("--limit", type=int, default=0, help="Batasi jumlah data; 0 berarti seluruh data")
    parser.add_argument("--start", type=int, default=0, help="Mulai dari offset katalog BPOM")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    checked_at = datetime.now(timezone.utc)
    totals = {"seen": 0, "inserted": 0, "updated": 0}
    with httpx.Client(timeout=60, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
        page = client.get(BPOM_LIST_URL)
        page.raise_for_status()
        match = re.search(r'name="csrf-token" content="([^"]+)', page.text)
        if not match:
            raise RuntimeError("Token halaman BPOM tidak ditemukan")
        token = match.group(1)
        first = fetch_page(client, token, 0, min(args.batch_size, args.limit or args.batch_size))
        available = int(first.get("recordsFiltered") or first.get("recordsTotal") or 0)
        start_at = max(0, min(args.start, available))
        remaining = available - start_at
        target = min(remaining, args.limit) if args.limit else remaining
        print(
            f"BPOM tersedia: {available}; mulai: {start_at}; target proses: {target}; "
            f"dry_run: {args.dry_run}"
        )

        start = start_at
        while totals["seen"] < target:
            length = min(args.batch_size, target - totals["seen"])
            payload = first if start == 0 and length == len(first.get("data", [])) else fetch_page(client, token, start, length)
            mapped = [map_product(row, checked_at) for row in payload.get("data", [])]
            mapped = mapped[: target - totals["seen"]]
            if not mapped:
                break
            if not args.dry_run:
                inserted, updated = upsert_batch(mapped)
                totals["inserted"] += inserted
                totals["updated"] += updated
            totals["seen"] += len(mapped)
            print(
                f"{totals['seen']}/{target} | baru: {totals['inserted']} | "
                f"diperbarui: {totals['updated']}"
            )
            start += len(mapped)
            if totals["seen"] < target:
                time.sleep(max(args.delay, 0))

    print(f"Selesai: {totals}")


if __name__ == "__main__":
    main()
