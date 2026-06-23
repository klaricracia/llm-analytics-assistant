"""
LLM Analytics Assistant
=======================
Author: Klarissa Artavia — Data & AI Strategy
GitHub: https://github.com/klaricracia
LinkedIn: https://www.linkedin.com/in/klariartavia/

A conversational AI interface over three connected retail analytics projects:
  - Project 1: Customer RFM Segmentation
  - Project 2: KPI Monitoring Bot
  - Project 3: Dynamic Pricing Engine

Ask questions in plain English. The assistant routes to the right tool,
queries the data, and returns a grounded, narrative answer.

Usage:
    python assistant.py                    # interactive CLI mode
    python assistant.py --demo             # runs preset demo questions
    from assistant import ask              # use as a module in app.py
"""

import os
import anthropic
from typing import Optional
from tools.customer_tools import (
    get_segment_overview, get_segment_detail, get_at_risk_summary,
    get_top_customers, get_revenue_concentration,
)
from tools.kpi_tools import (
    get_alert_summary, get_recent_alerts, get_alerts_by_kpi,
    get_worst_anomaly,
)
from tools.pricing_tools import (
    get_pricing_summary, get_top_opportunities, get_products_by_action,
    get_category_pricing_summary, get_model_performance,
)

# ── Tool registry ──────────────────────────────────────────────────────────────
TOOLS = [
    {
        "name": "get_segment_overview",
        "description": "Get a full overview of all 8 customer segments: customer counts, revenue share, recency, and average spend. Use for general questions about customer base or segments.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_segment_detail",
        "description": "Get detailed statistics for one specific customer segment.",
        "input_schema": {
            "type": "object",
            "properties": {"segment_name": {"type": "string", "description": "Segment name: Champions, Loyal Customers, Potential Loyalists, Promising, At Risk, Can't Lose Them, Hibernating, or Lost"}},
            "required": ["segment_name"],
        },
    },
    {
        "name": "get_at_risk_summary",
        "description": "Get focused analysis of high-value customers showing churn signals (At Risk and Can't Lose Them segments).",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_top_customers",
        "description": "Get the top N customers ranked by total lifetime spend.",
        "input_schema": {
            "type": "object",
            "properties": {"n": {"type": "integer", "description": "Number of top customers to return (default 10)"}},
            "required": [],
        },
    },
    {
        "name": "get_revenue_concentration",
        "description": "Analyse how concentrated total revenue is across segments — highlights customer dependency risk.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_alert_summary",
        "description": "Get an overall summary of all KPI anomalies detected by the monitoring bot.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_recent_alerts",
        "description": "Get KPI anomaly alerts from the last N days of data.",
        "input_schema": {
            "type": "object",
            "properties": {"days": {"type": "integer", "description": "Number of days to look back (default 90)"}},
            "required": [],
        },
    },
    {
        "name": "get_alerts_by_kpi",
        "description": "Get all historical alerts for a specific KPI (revenue, new customers, at-risk customers, etc.).",
        "input_schema": {
            "type": "object",
            "properties": {"kpi_name": {"type": "string", "description": "KPI name to filter by"}},
            "required": ["kpi_name"],
        },
    },
    {
        "name": "get_worst_anomaly",
        "description": "Get the single worst KPI anomaly detected across all data.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_pricing_summary",
        "description": "Get an overview of ML pricing recommendations for all 50 products.",
        "input_schema": {
            "type": "object",
            "properties": {"objective": {"type": "string", "enum": ["margin","revenue"], "description": "Optimisation objective"}},
            "required": [],
        },
    },
    {
        "name": "get_top_opportunities",
        "description": "Get the top N products with the highest pricing uplift opportunity.",
        "input_schema": {
            "type": "object",
            "properties": {
                "n": {"type": "integer", "description": "Number of products (default 5)"},
                "objective": {"type": "string", "enum": ["margin","revenue"]},
            },
            "required": [],
        },
    },
    {
        "name": "get_products_by_action",
        "description": "Get all products recommended to RAISE, LOWER, or HOLD their price.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["RAISE","LOWER","HOLD"]},
                "objective": {"type": "string", "enum": ["margin","revenue"]},
            },
            "required": ["action"],
        },
    },
    {
        "name": "get_category_pricing_summary",
        "description": "Get pricing recommendations aggregated by product category.",
        "input_schema": {
            "type": "object",
            "properties": {"objective": {"type": "string", "enum": ["margin","revenue"]}},
            "required": [],
        },
    },
    {
        "name": "get_model_performance",
        "description": "Get the XGBoost demand model's performance metrics (R², MAE, MAPE) and top feature importances.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

# ── Tool dispatcher ────────────────────────────────────────────────────────────
def dispatch(name: str, inputs: dict) -> str:
    fns = {
        "get_segment_overview":       lambda: get_segment_overview(),
        "get_segment_detail":         lambda: get_segment_detail(inputs.get("segment_name","")),
        "get_at_risk_summary":        lambda: get_at_risk_summary(),
        "get_top_customers":          lambda: get_top_customers(inputs.get("n",10)),
        "get_revenue_concentration":  lambda: get_revenue_concentration(),
        "get_alert_summary":          lambda: get_alert_summary(),
        "get_recent_alerts":          lambda: get_recent_alerts(inputs.get("days",90)),
        "get_alerts_by_kpi":          lambda: get_alerts_by_kpi(inputs.get("kpi_name","")),
        "get_worst_anomaly":          lambda: get_worst_anomaly(),
        "get_pricing_summary":        lambda: get_pricing_summary(inputs.get("objective","margin")),
        "get_top_opportunities":      lambda: get_top_opportunities(inputs.get("n",5), inputs.get("objective","margin")),
        "get_products_by_action":     lambda: get_products_by_action(inputs.get("action","RAISE"), inputs.get("objective","margin")),
        "get_category_pricing_summary":lambda: get_category_pricing_summary(inputs.get("objective","margin")),
        "get_model_performance":      lambda: get_model_performance(),
    }
    fn = fns.get(name)
    return fn() if fn else f"Unknown tool: {name}"


# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM = """You are an AI analytics assistant built on top of three retail data projects:

1. CUSTOMER SEGMENTATION (RFM analysis): 4,338 customers segmented into 8 tiers — Champions, Loyal Customers, Potential Loyalists, Promising, At Risk, Can't Lose Them, Hibernating, Lost.

2. KPI MONITORING BOT: Automated anomaly detection across 6 KPIs — daily revenue, average order value, new customers, at-risk customers, lost customers, and stockout events. Uses z-score statistical detection with a 14-day rolling window.

3. DYNAMIC PRICING ENGINE: XGBoost demand model (R² = 0.9483) trained on 18,250 observations across 50 products in 5 categories. Price optimiser finds the price that maximises margin or revenue per product.

Your job is to answer business questions clearly and concisely using the available tools. Always:
- Lead with the key number or finding
- Interpret the data in business terms, not just report raw numbers
- If a question spans multiple datasets, call multiple tools
- Keep answers focused — no unnecessary padding
- If asked for a recommendation, give one

Built by Klarissa Artavia · Data & AI Strategy"""


# ── Core ask function ──────────────────────────────────────────────────────────
def ask(
    question: str,
    history: Optional[list] = None,
    api_key: Optional[str] = None,
) -> str:
    """
    Ask a business question. Returns the assistant's answer as a string.

    Args:
        question: The business question in plain English
        history:  Optional list of prior (user, assistant) message pairs for context
        api_key:  Anthropic API key (falls back to ANTHROPIC_API_KEY env var)
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return "Error: ANTHROPIC_API_KEY not set. Add it to your .env file or pass it directly."

    client   = anthropic.Anthropic(api_key=key)
    messages = []

    # Inject conversation history
    if history:
        for user_msg, asst_msg in history:
            messages.append({"role": "user",      "content": user_msg})
            messages.append({"role": "assistant", "content": asst_msg})

    messages.append({"role": "user", "content": question})

    # Agentic tool-use loop
    while True:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=2048,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
        )

        # Collect any text from this turn
        text_parts = [b.text for b in response.content if b.type == "text"]

        if response.stop_reason == "end_turn":
            return "\n".join(text_parts) if text_parts else "(no response)"

        if response.stop_reason == "tool_use":
            # Add assistant's response to history
            messages.append({"role": "assistant", "content": response.content})

            # Execute all tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = dispatch(block.name, block.input)
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result,
                    })

            messages.append({"role": "user", "content": tool_results})
            continue

        # Unexpected stop reason
        return "\n".join(text_parts) if text_parts else "(unexpected stop)"


# ── CLI ────────────────────────────────────────────────────────────────────────
DEMO_QUESTIONS = [
    "Give me an overview of our customer segments. Which ones should I focus on?",
    "How much revenue is at risk from churning customers?",
    "What KPI anomalies were detected? Which was the worst?",
    "Which products have the biggest pricing opportunity if I want to maximise margin?",
    "How well does the pricing model predict demand?",
    "If I wanted to grow revenue instead of margin, what would change?",
]

if __name__ == "__main__":
    import argparse, textwrap
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Run preset demo questions")
    args = parser.parse_args()

    print("\n" + "="*62)
    print("  LLM ANALYTICS ASSISTANT — Klarissa Artavia")
    print("="*62)

    history = []

    if args.demo:
        for q in DEMO_QUESTIONS:
            print(f"\n❓ {q}")
            print("─"*60)
            answer = ask(q, history=history)
            print(textwrap.fill(answer, width=70, subsequent_indent="   "))
            history.append((q, answer))
            print()
    else:
        print("  Ask any question about customers, KPIs, or pricing.")
        print("  Type 'exit' to quit.\n")
        while True:
            try:
                q = input("❓ You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye."); break
            if q.lower() in ("exit","quit","q"):
                print("Goodbye."); break
            if not q:
                continue
            print("\n🤖 Assistant:")
            answer = ask(q, history=history)
            print(textwrap.fill(answer, width=70, subsequent_indent="   "))
            history.append((q, answer))
            print()
