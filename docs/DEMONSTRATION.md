# Demonstration Scenarios

Structured scenarios for system review and live demonstration. Default farmer profile: **F001 (Ramesh Kumar, Warangal, cotton)** unless noted.

## Scenario 1: Pest diagnosis and escalation

**Query:** `Why are my cotton leaves turning yellow?`

**Expected behaviour:**
- Intent: `pest_disease`
- RAG cites cotton pest guides
- Confidence badge displayed
- Possible escalation if outbreak keywords match

**Talking points:** Personalized to district weather; cites approved guides; expert path for outbreak risk.

---

## Scenario 2: Weather-aware irrigation

**Farmer:** F005 (Mohan Lal, Jalandhar)

**Query:** `When should I irrigate wheat given current weather and crop stage?`

**Expected behaviour:**
- Intent: `irrigation`
- Context includes rainfall and crop stage
- Weather-aware steps from wheat knowledge base

---

## Scenario 3: Fertilizer schedule

**Farmer:** F002 (Sunita Devi, Guntur)

**Query:** `What is the recommended fertilizer schedule for paddy in Guntur district?`

**Expected behaviour:**
- Intent: `input_recommendation`
- Soil context attached
- Paddy guide nitrogen schedule cited

---

## Scenario 4: Market price comparison

**Farmer:** F003 (Vikram Singh, Nashik)

**Query:** `What is today's tomato market price and nearby mandi comparison?`

**Expected behaviour:**
- Intent: `market_price`
- Nashik APMC price from CSV integration
- Mandi comparison in response context

---

## Scenario 5: Insurance claim guidance

**Query:** `How do I file crop insurance claim after heavy rainfall damage?`

**Expected behaviour:**
- Intent: `insurance`
- RAG from insurance knowledge base
- Likely escalation with safety disclaimer

---

## Scenario 6: Field officer case review

**Setup:** Execute Scenario 1, then open **Human Review** as field officer.

**Expected behaviour:** Open case with AI summary, district, crop, and follow-up workflow.

---

## Scenario 7: Outbreak cluster detection

**Setup:** Submit two or more pest/disease queries for Warangal cotton, then run **Analytics → Pest outbreak detection**.

**Expected behaviour:** Outbreak alert row for Warangal with query count and farmer participation metrics.

---

## Scenario 8: Voice input (optional)

**Location:** AI Crop Advisor → Voice question panel

**Steps:** Record a short question → confirm transcription → submit.

**Expected behaviour:** Same pipeline as typed input. Requires `SpeechRecognition` and internet for Google Speech API.

---

## Scenario 9: Scheme payment status

**Location:** AI Crop Advisor → Schemes and payments

**Expected behaviour:** PM-KISAN demo row with installment dates. Clearly labeled as demonstration data.

---

## Scenario 10: Input dealer request

**Location:** AI Crop Advisor → Input dealers

**Steps:** Select input type → view licensed dealers → submit demo quote request.

**Expected behaviour:** Safety warning, district dealer list, request saved to SQLite.

---

## Scenario 11: New farmer registration

**Location:** Sign Up (`pages/00_Sign_Up.py`)

**Steps:** Enter name, district, crop, phone; accept consent.

**Expected behaviour:** New farmer profile created; self-entered data only.

---

## Additional demonstrations

### Multilingual support

Set sidebar language to Telugu or Hindi. Submit an English query. Response should appear in the selected language.

### Governance audit

Open **Governance** and export audit CSV showing model, confidence, and guardrail flags.

### Knowledge administration

Open **Knowledge** → re-ingest knowledge base → test query `bollworm cotton` to verify RAG retrieval.

## Pre-demonstration checklist

```powershell
python scripts/smoke_test.py
python scripts/eval_intent_classification.py
streamlit run app.py
```

Verify demo credentials: `farmer_f001` / `farmer123`, `officer1` / `officer2026`, `admin` / `admin2026`.
