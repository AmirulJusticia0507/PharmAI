const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface Drug {
  id: number;
  name: string;
  generic_name: string | null;
  category: string | null;
  description: string | null;
  dosage_form: string | null;
  manufacturer: string | null;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

export async function fetchDrugs(params?: {
  search?: string;
  category?: string;
  skip?: number;
  limit?: number;
}): Promise<Drug[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set("search", params.search);
  if (params?.category) query.set("category", params.category);
  if (params?.skip) query.set("skip", String(params.skip));
  if (params?.limit) query.set("limit", String(params.limit));

  const res = await fetch(`${API_BASE}/api/drugs?${query}`);
  if (!res.ok) throw new Error("Gagal mengambil data obat");
  return res.json();
}

export async function fetchDrug(id: number): Promise<Drug> {
  const res = await fetch(`${API_BASE}/api/drugs/${id}`);
  if (!res.ok) throw new Error("Obat tidak ditemukan");
  return res.json();
}

export async function createDrug(data: Partial<Drug>): Promise<Drug> {
  const res = await fetch(`${API_BASE}/api/drugs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Gagal membuat data obat");
  return res.json();
}
