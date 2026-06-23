# LLM Analytics Assistant

**Natural language interface over three connected retail analytics projects.**

Ask a business question in plain English. The assistant decides which data tool to call, queries the relevant dataset, and returns a grounded answer — no SQL, no dashboards.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Claude API](https://img.shields.io/badge/Claude-claude--opus--4--8-8B5CF6?style=flat)](https://anthropic.com)
[![LangChain](https://img.shields.io/badge/LangChain-Tool_Use-1C3C3C?style=flat)](https://langchain.com)
[![Gradio](https://img.shields.io/badge/Gradio-Chat_UI-FF7C00?style=flat)](https://gradio.app)

---

## Problem

A retail team has RFM segmentation data, KPI anomaly logs, and ML pricing recommendations sitting in three separate CSV files. Getting answers requires knowing which file to query, writing code, and interpreting statistical outputs. Most business stakeholders can't do that — so the data sits unused.

**The question:** can a single conversational interface make three separate analytics systems accessible to anyone?

---

## Approach

The assistant is built on Anthropic's native tool-use API. Claude receives a plain-English question and a registry of 14 Python functions. It chooses which functions to call (often chaining multiple), executes them against the real data, and synthesises the results into a business-readable answer.

```
User question
     │
     ▼
Claude (claude-opus-4-8) — reasons about intent
     │
     ▼
Tool calls (1 or more, in parallel or sequence)
     │
     ▼
Python functions query CSV data
     │
     ▼
Claude synthesises results → business answer
```

The agentic loop continues until `stop_reason == "end_turn"` — meaning Claude keeps calling tools until it has everything it needs to answer.

---

## Connected Data Sources

| Source | Dataset | Records |
|--------|---------|---------|
| [Retail Customer RFM Analysis](https://github.com/klaricracia/retail-customer-rfm-analysis) | 4,338 customers across 8 segments | rfm_segments.csv |
| [KPI Monitoring Bot](https://github.com/klaricracia/kpi-monitoring-bot) | 365 days of KPI anomaly logs | alert_log.csv |
| [Dynamic Pricing Model](https://github.com/klaricracia/dynamic-pricing-model) | 50 products, ML pricing recs for 2 objectives | pricing_recommendations.csv, model_metrics.json |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Anthropic Claude (claude-opus-4-8) |
| Agent framework | Native Anthropic tool-use API |
| Data tools | Python + pandas |
| Chat UI | Gradio |
| Configuration | python-dotenv |

---

## Tool Registry (14 tools)

**Customer Intelligence**
- `get_segment_overview()` — all 8 RFM segments with counts, revenue, recency
- `get_segment_detail(segment_name)` — deep dive into one segment
- `get_at_risk_summary()` — revenue at risk from churning customers
- `get_top_customers(n)` — top customers by lifetime spend
- `get_revenue_concentration()` — revenue distribution / dependency risk

**KPI Monitoring**
- `get_alert_summary()` — all anomaly alerts overview
- `get_recent_alerts(days)` — alerts from the last N days
- `get_alerts_by_kpi(kpi_name)` — all alerts for a specific KPI
- `get_worst_anomaly()` — highest z-score event detected

**Pricing Engine**
- `get_pricing_summary(objective)` — overview for margin or revenue objective
- `get_top_opportunities(n, objective)` — highest-uplift products
- `get_products_by_action(action, objective)` — RAISE / LOWER / HOLD lists
- `get_category_pricing_summary(objective)` — aggregated by category
- `get_model_performance()` — XGBoost R², MAE, MAPE, feature importances

---

## Results

Example questions the assistant answers correctly:

> *"How much revenue is at risk from churning customers?"*
> → **$1.64M across 189 customers** — with breakdown by segment and recommended action

> *"What was the worst KPI anomaly detected?"*
> → **Daily Revenue +80% on 2024-04-30**, z-score 6.77 — with business context

> *"Which products have the biggest margin opportunity? What changes if I optimise for revenue instead?"*
> → Named products, price deltas, and a clear explanation of why the two objectives produce opposite recommendations

The assistant handles **multi-tool questions** in a single turn — it chains calls automatically when the question spans multiple datasets.

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/klaricracia/llm-analytics-assistant
cd llm-analytics-assistant
```

**2. Install dependencies**
```bash
pip install anthropic gradio pandas python-dotenv
```

**3. Add your API key**
```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=your_key_here
```

**4. Run the Gradio chat interface**
```bash
python app.py
# Open http://localhost:7860
```

**Or run the CLI demo**
```bash
python assistant.py --demo
```

---

## Project Structure

```
llm-analytics-assistant/
├── assistant.py          # Core agent — tool registry, dispatch, agentic loop
├── app.py                # Gradio chat UI
├── tools/
│   ├── customer_tools.py # 5 RFM segmentation query functions
│   ├── kpi_tools.py      # 4 anomaly alert query functions
│   └── pricing_tools.py  # 5 pricing recommendation query functions
├── data/                 # CSV outputs from Projects 1–3
├── dashboard/index.html  # Static demo (GitHub Pages)
└── .env.example          # API key template
```

---

## Learnings

- **Tool-use is more reliable than RAG for structured data.** Rather than embedding CSV content in a vector store, defining typed Python functions and letting the LLM choose which to call produces more accurate, auditable answers.
- **Multi-tool chaining requires clear tool descriptions.** The quality of Claude's routing decisions is almost entirely determined by how well each tool's purpose is described.
- **The agentic loop is simple to implement.** Anthropic's `stop_reason == "tool_use"` pattern handles all multi-step reasoning without a framework — `assistant.py` is ~100 lines.
- **Connecting separate projects creates disproportionate value.** Each project alone answers one type of question. Together, they enable questions like "which at-risk customers are in the categories where I have the most pricing headroom?" — something no single tool could answer.

---

## Part of a 4-Project Portfolio

| # | Project | Focus |
|---|---------|-------|
| 1 | [Retail Customer RFM Analysis](https://github.com/klaricracia/retail-customer-rfm-analysis) | Customer segmentation |
| 2 | [KPI Monitoring Bot](https://github.com/klaricracia/kpi-monitoring-bot) | Anomaly detection |
| 3 | [Dynamic Pricing Model](https://github.com/klaricracia/dynamic-pricing-model) | ML price optimisation |
| **4** | **LLM Analytics Assistant** | **Natural language interface** |

---

**Built by [Klarissa Artavia](https://www.linkedin.com/in/klariartavia/) · Data & AI Strategy**
