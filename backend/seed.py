from app.database import SessionLocal
from app.models import Drug

drugs_data = [
    {
        "name": "Paracetamol 500mg",
        "generic_name": "Paracetamol",
        "category": "Analgesik & Antipiretik",
        "description": "Obat penurun panas dan pereda nyeri. Digunakan untuk demam, sakit kepala, dan nyeri ringan.",
        "dosage_form": "Tablet",
        "manufacturer": "Kimia Farma",
    },
    {
        "name": "Amoxicillin 500mg",
        "generic_name": "Amoxicillin",
        "category": "Antibiotik",
        "description": "Antibiotik golongan penisilin untuk infeksi bakteri seperti ISPA, infeksi saluran kemih, dan kulit.",
        "dosage_form": "Kapsul",
        "manufacturer": "Sanbe Farma",
    },
    {
        "name": "Omeprazole 20mg",
        "generic_name": "Omeprazole",
        "category": "Antasida & PPI",
        "description": "Penghambat pompa proton untuk mengatasi maag, GERD, dan tukak lambung.",
        "dosage_form": "Kapsul",
        "manufacturer": "Pharos",
    },
    {
        "name": "Cetirizine 10mg",
        "generic_name": "Cetirizine",
        "category": "Antihistamin",
        "description": "Antihistamin untuk alergi seperti pilek, bersin-bersin, dan gatal-gatal.",
        "dosage_form": "Tablet",
        "manufacturer": "Dexa Medica",
    },
    {
        "name": "Metformin 500mg",
        "generic_name": "Metformin HCl",
        "category": "Antidiabetes",
        "description": "Obat untuk mengontrol kadar gula darah pada pasien diabetes tipe 2.",
        "dosage_form": "Tablet",
        "manufacturer": "Kimia Farma",
    },
    {
        "name": "Amlodipine 5mg",
        "generic_name": "Amlodipine Besylate",
        "category": "Antihypertensi",
        "description": "Obat untuk menurunkan tekanan darah tinggi dan mengatasi angina.",
        "dosage_form": "Tablet",
        "manufacturer": "Novell Pharmaceutical",
    },
    {
        "name": "Salbutamol 4mg",
        "generic_name": "Salbutamol",
        "category": "Bronkodilator",
        "description": "Obat untuk meredakan gejala asma dan penyakit paru obstruktif kronis (PPOK).",
        "dosage_form": "Tablet",
        "manufacturer": "GlaxoSmithKline",
    },
    {
        "name": "Ibuprofen 400mg",
        "generic_name": "Ibuprofen",
        "category": "NSAID",
        "description": "Obat antiinflamasi nonsteroid untuk pereda nyeri dan antiinflamasi.",
        "dosage_form": "Tablet",
        "manufacturer": "Sanbe Farma",
    },
    {
        "name": "ORS sachet",
        "generic_name": "Oral Rehydration Salts",
        "category": "Elektrolit",
        "description": "Serbuk untuk cairan rehidrasi oral, mengatasi diare dan dehidrasi.",
        "dosage_form": "Serbuk",
        "manufacturer": "Various",
    },
    {
        "name": "Vitamin C 1000mg",
        "generic_name": "Asam Askorbat",
        "category": "Suplemen",
        "description": "Suplemen vitamin C untuk daya tahan tubuh dan antioksidan.",
        "dosage_form": "Tablet hisap",
        "manufacturer": "Youvit",
    },
]


def seed():
    db = SessionLocal()
    try:
        existing = db.query(Drug).count()
        if existing > 0:
            print(f"Database sudah ada {existing} data obat. Skip seed.")
            return

        for data in drugs_data:
            db.add(Drug(**data))
        db.commit()
        print(f"Berhasil seed {len(drugs_data)} data obat.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
