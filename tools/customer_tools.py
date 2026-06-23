"""
Customer Intelligence Tools
Queries the RFM segmentation data from Project 1.
"""
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def _load():
    rfm = pd.read_csv(DATA_DIR / "rfm_segments.csv")
    summary = pd.read_csv(DATA_DIR / "segment_summary.csv")
    return rfm, summary


def get_segment_overview() -> str:
    """Returns a full overview of all customer segments with key metrics."""
    rfm, summary = _load()
    total_customers = len(rfm)
    total_revenue   = rfm["Monetary"].sum()

    lines = [f"CUSTOMER SEGMENT OVERVIEW — {total_customers:,} customers, ${total_revenue:,.0f} total revenue\n"]
    order = ["Champions","Loyal Customers","Potential Loyalists","Promising",
             "At Risk","Can't Lose Them","Hibernating","Lost"]

    for seg in order:
        row = summary[summary["Segment"] == seg]
        if row.empty: continue
        r = row.iloc[0]
        share = r["Total_Revenue"] / total_revenue * 100
        lines.append(
            f"  {seg:<22} {int(r['Customers']):>5} customers | "
            f"Avg recency {r['Avg_Recency']:.0f}d | "
            f"Avg spend ${r['Avg_Monetary']:,.0f} | "
            f"{share:.1f}% of revenue"
        )
    return "\n".join(lines)


def get_segment_detail(segment_name: str) -> str:
    """Returns detailed statistics for a specific customer segment."""
    rfm, summary = _load()
    seg_name = segment_name.strip().title()
    row = summary[summary["Segment"].str.lower() == seg_name.lower()]

    if row.empty:
        available = summary["Segment"].tolist()
        return f"Segment '{segment_name}' not found. Available: {', '.join(available)}"

    r = row.iloc[0]
    customers = rfm[rfm["Segment"].str.lower() == seg_name.lower()]
    total_rev = rfm["Monetary"].sum()

    return (
        f"SEGMENT: {r['Segment']}\n"
        f"  Customers:        {int(r['Customers']):,}\n"
        f"  % of base:        {int(r['Customers'])/len(rfm)*100:.1f}%\n"
        f"  Avg recency:      {r['Avg_Recency']:.0f} days since last purchase\n"
        f"  Avg orders:       {r['Avg_Frequency']:.1f} orders\n"
        f"  Avg spend:        ${r['Avg_Monetary']:,.0f}\n"
        f"  Total revenue:    ${r['Total_Revenue']:,.0f}\n"
        f"  Revenue share:    {r['Total_Revenue']/total_rev*100:.1f}%\n"
        f"  RFM score range:  R={customers['R_Score'].mean():.1f} "
        f"F={customers['F_Score'].mean():.1f} M={customers['M_Score'].mean():.1f}"
    )


def get_at_risk_summary() -> str:
    """Returns focused analysis of At Risk and Can't Lose Them segments — high-value customers showing churn signals."""
    rfm, summary = _load()
    total_rev = rfm["Monetary"].sum()

    at_risk   = summary[summary["Segment"] == "At Risk"]
    cant_lose = summary[summary["Segment"] == "Can't Lose Them"]

    lines = ["HIGH-VALUE CHURN RISK SUMMARY\n"]
    for label, row in [("At Risk", at_risk), ("Can't Lose Them", cant_lose)]:
        if row.empty: continue
        r = row.iloc[0]
        lines.append(
            f"  {label}: {int(r['Customers'])} customers | "
            f"${r['Total_Revenue']:,.0f} revenue at risk ({r['Total_Revenue']/total_rev*100:.1f}%) | "
            f"Last purchase avg {r['Avg_Recency']:.0f} days ago | "
            f"Avg spend ${r['Avg_Monetary']:,.0f}"
        )
    lines.append(f"\n  Total at-risk revenue: ${(at_risk['Total_Revenue'].sum() + cant_lose['Total_Revenue'].sum()):,.0f}")
    lines.append("  Recommended action: personalised win-back campaign within 30 days")
    return "\n".join(lines)


def get_top_customers(n: int = 10) -> str:
    """Returns the top N customers by total lifetime spend."""
    rfm, _ = _load()
    top = rfm.nlargest(n, "Monetary")[["CustomerID","Segment","Recency","Frequency","Monetary","R_Score","F_Score","M_Score"]]
    lines = [f"TOP {n} CUSTOMERS BY LIFETIME SPEND\n"]
    for _, row in top.iterrows():
        lines.append(
            f"  Customer {int(row['CustomerID'])} | {row['Segment']:<22} | "
            f"${row['Monetary']:>9,.0f} | {int(row['Frequency'])} orders | "
            f"Last seen {int(row['Recency'])}d ago"
        )
    return "\n".join(lines)


def get_revenue_concentration() -> str:
    """Analyses how concentrated revenue is across segments — highlights dependency risk."""
    rfm, summary = _load()
    total = rfm["Monetary"].sum()
    top2  = summary.nlargest(2, "Total_Revenue")
    top2_rev = top2["Total_Revenue"].sum()

    return (
        f"REVENUE CONCENTRATION ANALYSIS\n"
        f"  Total revenue:          ${total:,.0f}\n"
        f"  Top 2 segments:         {top2['Segment'].tolist()}\n"
        f"  Top 2 segments revenue: ${top2_rev:,.0f} ({top2_rev/total*100:.1f}% of total)\n"
        f"  Segments count:         {len(summary)}\n"
        f"  Concentration risk:     {'HIGH — over 80% from 2 segments' if top2_rev/total > 0.8 else 'MODERATE'}"
    )
