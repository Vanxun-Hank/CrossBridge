# CrossBridge AI Project Memory

Last updated: 2026-05-22

## Competition Context

- Competition: BOCHK Challenge 2026 / 中銀香港創新先驅大賽 2026.
- Official positioning: build innovative solutions for financial-industry pain points or business opportunities.
- Eligible teams: 2-5 members, student stream or startup stream.
- Proposal submission: PDF, email size under 10MB, due on or before 2026-06-15.
- Required theme structure: choose at least one technology theme and at least one finance scenario theme.
- Technology themes: Generative AI, Blockchain, Big Data, Quantum Computing.
- Scenario themes: Inclusive Finance, Payment, Risk Management, ESG, Cross Border (Mainland, Southeast Asia, and other overseas regions).

## Current Idea

CrossBridge AI is a B2B cross-border financial decision assistant for SMEs expanding across Hong Kong, the Greater Bay Area, mainland China, Southeast Asia, and other overseas markets.

Core positioning:

- Not a generic chatbot.
- Not a replacement for lawyers, accountants, relationship managers, or financial advisers.
- It provides preliminary, source-backed cross-border financial intelligence, reducing SME research cost and helping banks improve qualified SME lending conversion.

Best competition fit:

- Technology: Generative AI + Big Data.
- Scenario: Cross Border + Inclusive Finance + Risk Management.

## Teammate MVP In `files/`

Current implementation files:

- `files/README.md`: MVP description, setup instructions, roadmap notes.
- `files/app.py`: Streamlit demo UI.
- `files/rag_engine.py`: RAG engine with semantic retrieval fallback to TF-IDF and optional LLM generation.
- `files/knowledge_base.json`: structured demo knowledge base.
- `files/requirements.txt`: Python dependencies.
- `files/crossbridge_mvp.zip`: packaged copy of the same MVP.

Current MVP capability:

- User asks a cross-border finance question.
- System filters by region and topic.
- RAG retrieves relevant entries from a structured knowledge base.
- LLM or fallback template returns an answer with citations.
- Demo has a no-API fallback mode, which is useful for unstable pitch-day network conditions.

Important caveat:

- `knowledge_base.json` currently contains sample data and explicitly marks several entries as non-authoritative demo content.
- Before using this in a competition pitch, replace or clearly separate the demo data with real official sources.

Local status checked on 2026-05-22:

- The `.venv` exists but dependencies are not installed.
- `rag_engine.py` currently fails locally because `numpy` is missing.
- `.venv/bin/streamlit` is not present.
- The current `.venv` points to `python3.14`, which may create package compatibility risk. Prefer recreating with Python 3.12 for a safer demo environment.

## Product Roadmap

### Phase 1: Source-backed Q&A

Goal: make the current RAG demo credible.

Required work:

- Replace sample knowledge entries with real official sources.
- Add metadata: jurisdiction, topic, source URL, publish date, effective date, last checked date, source type, disclaimer level.
- Add answer guardrails: "insufficient source" response, no legal/financial advice, no unsupported numeric claims.
- Add a small evaluation set of typical SME questions.

### Phase 2: Cross-border Payment Assistant

Goal: move from "explaining policy" to "supporting payment decisions".

Functions:

- Compare remittance routes by estimated fee, FX spread, settlement time, required documents, and risk flags.
- Explain why a transaction may trigger enhanced due diligence.
- Generate a document checklist for cross-border payment.

Technology:

- Structured fee/rate tables.
- FX API or manually refreshed rate sample for demo.
- Deterministic rules engine for calculations.
- LLM only for explanation, not for fee computation.

### Phase 3: SME Loan Readiness

Goal: connect SME cross-border questions to bank financing opportunities.

Functions:

- Ask for company age, revenue, industry, trade frequency, bank statements, invoices, receivables, and target market.
- Estimate readiness rather than final credit approval.
- Recommend likely financing paths: SME loan, trade finance, invoice financing, or guarantee-backed products.
- Generate a relationship-manager summary.

Technology:

- Rule-based scorecard for MVP.
- Optional explainable ML later.
- Document parser for invoices, bank statements, and trade documents.
- Privacy-preserving consent flow.

### Phase 4: Market Entry Navigator

Goal: help SMEs understand jurisdiction-specific setup and banking requirements.

Functions:

- Company setup checklist.
- Banking onboarding checklist.
- Tax and licensing considerations.
- Market entry risk summary.

Technology:

- Workflow engine.
- Jurisdiction taxonomy.
- RAG over official market-entry and regulator documents.

## Data Needed

Minimum viable sources:

- BOCHK SME products, remittance charges, business banking onboarding pages.
- HKMA guidance, Commercial Data Interchange material, AML/CFT and cross-border payment guidance.
- SME Financing Guarantee Scheme official materials.
- Hong Kong Companies Registry, Inland Revenue Department, InvestHK, HKTDC / GoGBA.
- Mainland China foreign exchange and market-entry materials from official regulators.
- Southeast Asia central banks, tax authorities, business registration agencies, and investment promotion agencies.
- FX and remittance pricing data for demo calculations.

Internal or simulated data for pitch:

- Synthetic SME company profiles.
- Synthetic bank statements, invoices, receivables, and trade flows.
- A small benchmark question set with expected citations and ideal answers.

## Business Knowledge To Strengthen

- SME lending basics: working capital loan, trade finance, invoice financing, guarantee schemes, collateral, tenor, interest, repayment.
- Cross-border payment basics: SWIFT, CHATS/RTGS, FPS, correspondent bank charges, cut-off time, FX spread, remittance purpose.
- Bank risk controls: KYC, KYB, AML, sanctions screening, CDD, EDD, transaction monitoring.
- Market entry: company incorporation, tax registration, licensing, bank account opening, foreign exchange controls.
- AI governance in finance: hallucination control, citation quality, privacy, audit trail, human review.

## Recommended Pitch Demo Flow

Scenario: A Hong Kong SME wants to pay a Vietnam supplier and expand into Shenzhen and Vietnam.

Demo sequence:

1. Ask a policy/compliance question and return a cited answer.
2. Show required documents and red flags for the payment.
3. Compare two or three remittance options.
4. Ask a few SME finance questions and output loan-readiness status.
5. Generate a bank relationship-manager summary for follow-up.

This flow proves both sides of the business value:

- SMEs save time and reduce uncertainty.
- BOCHK gains better-prepared SME leads and improves lending workflow efficiency.
