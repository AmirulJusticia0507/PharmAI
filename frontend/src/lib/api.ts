const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface Drug {
  id: number;
  name: string;
  generic_name: string | null;
  category: string | null;
  description: string | null;
  dosage_form: string | null;
  indication: string | null;
  benefit: string | null;
  dosage: string | null;
  usage_time: string[] | null;
  frequency: string | null;
  manufacturer: string | null;
  image_url: string | null;
  active_ingredients: string[];
  registration_number: string | null;
  registration_status: string;
  registration_expires_at: string | null;
  regulatory_source_url: string | null;
  regulatory_checked_at: string | null;
  regulatory_notes: string | null;
  source_product_id: string | null;
  source_application_id: string | null;
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

export async function fetchDrugCount(search?: string): Promise<number> {
  const query = new URLSearchParams();
  if (search) query.set("search", search);
  const res = await fetch(`${API_BASE}/api/drugs/count?${query}`);
  if (!res.ok) throw new Error("Gagal mengambil jumlah obat");
  const data = await res.json();
  return data.total;
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

export interface DrugAnalysis {
  indication: string;
  benefit: string;
  dosage: string;
  usage_time: string[];
  frequency: string;
  confidence: number;
}

export async function fetchDrugAnalysis(drugId: number): Promise<DrugAnalysis> {
  const res = await fetch(`${API_BASE}/api/ai/analyze-drug`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ drug_id: drugId }),
  });
  if (!res.ok) throw new Error("Gagal menganalisis obat");
  return res.json();
}

export interface AgentStatus {
  running: boolean;
  processed: number;
  total: number;
  failed: number;
  current_drug: { id: number; name: string } | null;
  started_at: string | null;
  last_run: string | null;
  unanalyzed_count: number;
  analyzed_count: number;
}

export interface AgentRunResult {
  status: string;
  batch_size?: number;
  processed: number;
  failed: number;
  results: Array<{
    drug_id: number;
    name: string;
    status: "success" | "failed";
    confidence?: number;
    error?: string;
  }>;
}

export interface AgentTasks {
  running: boolean;
  tasks: AgentRunResult["results"];
  processed: number;
  failed: number;
  total: number;
  last_run: string | null;
}

export async function fetchAgentStatus(): Promise<AgentStatus> {
  const res = await fetch(`${API_BASE}/api/agent/status`);
  if (!res.ok) throw new Error("Gagal memeriksa status agent");
  return res.json();
}

export async function runAgentBatch(batchSize: number = 5): Promise<AgentRunResult> {
  const res = await fetch(`${API_BASE}/api/agent/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ batch_size: batchSize }),
  });
  if (!res.ok) throw new Error("Gagal menjalankan agent");
  return res.json();
}

export async function fetchAgentTasks(): Promise<AgentTasks> {
  const res = await fetch(`${API_BASE}/api/agent/tasks`);
  if (!res.ok) throw new Error("Gagal mengambil riwayat task");
  return res.json();
}

export async function clearAgentTasks(): Promise<{ status: string; tasks: [] }> {
  const res = await fetch(`${API_BASE}/api/agent/tasks/clear`);
  if (!res.ok) throw new Error("Gagal membersihkan task");
  return res.json();
}

export interface DrugVisualResult {
  image_url: string;
  revised_prompt: string;
  model: string;
  premium: boolean;
}

export async function generateDrugImage(
  drugId: number,
  usePremium: boolean = false,
): Promise<DrugVisualResult> {
  const res = await fetch(`${API_BASE}/api/ai/generate-drug-image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ drug_id: drugId, use_premium: usePremium }),
  });
  if (!res.ok) throw new Error("Gagal menghasilkan gambar obat");
  return res.json();
}
