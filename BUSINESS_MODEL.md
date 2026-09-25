# PharmAI Business Model

## 1. Premium Model

### Tiered Subscription

| Tier | Target | Price | Features |
|---|---|---|---|
| Free | Personal users | Rp 0/bulan | 10 scans/bulan, basic drug DB, simple interaction check |
| Pro | Pharmacists, medical students | Rp 49.000/bulan | Unlimited scans, batch drug analysis, advanced interaction, OCR, export PDF, drug catalog analytics |
| Pharmacy | Apotek owners | Rp 299.000/bulan | Multi-user (5 staff), patient history tracking, e-resep integration, inventory sync, white-label reports |
| Enterprise | HealthTech, pharma, hospitals | Custom | Full API access, custom AI models, SLA 99.9%, dedicated support, on-premise deployment |

### Premium Features

#### A. Enhanced AI Accuracy
- Multi-model ensemble: GPT-4o-mini + Claude 3 + specialized RxNorm
- Custom fine-tuning on Indonesian drug data (BPOM terminology)
- Confidence threshold blocking (<70% flagged for human review)

#### B. Batch Processing & Automation
- Agent mode: process entire drug catalog overnight
- Bulk import: CSV of medications auto-checked for interactions
- Scheduled reports: daily/weekly interaction reports

#### C. Advanced Analytics
- Drug utilization analytics: top prescribed drugs, seasonal trends
- Interaction network graph: visualize drug relationships
- Patient risk scoring: aggregate interaction risks per patient
- Inventory optimization: stock level recommendations

#### D. API Access (B2B)
- RESTful API: `/v1/drugs`, `/v1/scan`, `/v1/interactions`
- Webhooks for real-time critical interaction alerts
- Rate limit tiers: 1K/10K/100K calls/month
- SLA: 99.9% uptime, <500ms response

## 2. B2B Integration Scenarios

### A. Apotek (Retail Pharmacy) Integration

```
Apotek POS System
    --> Scan prescription (physical or e-resep)
    --> POST /v1/interactions {drugs: [...]}
    <-- {severity: "high", actions: ["warn", "contact_doctor"]}
    --> Pharmacist reviews before dispensing
```

Integration methods:
1. **API integration** - Apotek system calls PharmAI API
2. **Web widget** - Embeddable iframe
3. **Mobile SDK** - APK wrapper for apothecary apps

### B. EHR/EMR Integration

```
Doctor Orders New Prescription
    --> EHR submits to PharmAI
    POST /v1/patient-interactions
    {
      patient_id: "P-12345",
      current_drugs: [...],
      new_drug: "WARFARIN",
      diagnoses: ["atrial fibrillation", "hypertension"]
    }
    <-- {risk_level: "critical", interactions: [...]}
    --> EHR blocks order + alerts doctor
```

### C. HealthTech Platform Integration

```
User Scans Physical Pill
    --> POST /v1/scan-pill (image)
    <-- "METFORMIN 500mg"
    --> Auto-call /v1/analyze-drug
    --> Auto-call /v1/drug-info
    --> Show: drug info + side effects + nearby apotek
```

### D. Pharma Company Integration

```
Pharma Safety Team
    --> Monthly batch upload: new drug variants
    POST /v1/batch-verify
    --> Verify against BPOM + international pharmacopeia
    <-- {verified: 95%, discrepancies: [...]}
```

## 3. Partnership Scenarios

| Partner | Use Case | Revenue Model |
|---|---|---|
| BPOM | Official drug data provider | Government licensing |
| Kimia Farma/Guardian | In-store pharmacist tool | Rp 300K-1M/bulan per apotek |
| Hospital Network | Clinical decision support | Rp 5M-50M/year per hospital |
| BPJS/Asuransi | Prevent ADEs (claims reduction) | Shared savings (20-30%) |
| Universitas | Pharmacy education | Rp 50-100M/year per campus |

## 4. Implementation Requirements

### API Gateway & Security
- API Gateway for rate limiting, auth, logging
- OAuth 2.0 client credential flow
- Webhook HMAC validation
- AES-256 at-rest, TLS 1.3 in-transit

### Scalability
- Celery + Redis for batch processing
- Auto-scaling load balancer
- Redis cache (90% hit rate)
- Multi-region (Singapore, Jakarta)

### Compliance
- ISO 13485 (medical device QMS)
- GDPR-equivalent data protection
- BPOM drug info accuracy

## 5. Monetization Timeline

```
Phase 1 (6mo):  Pro tier     --> 50 subs     --> Rp 2.5M MRR
Phase 2 (12mo): B2B pilot   --> 3 enterprise --> Rp 150M/yr
Phase 3 (24mo): Scale up    --> 50+ B2B      --> Rp 5B ARR
```
