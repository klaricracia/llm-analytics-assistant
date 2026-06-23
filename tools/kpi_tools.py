"""
KPI Monitoring Tools
Queries the anomaly alert log from Project 2.
"""
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def _load():
    df = pd.read_csv(DATA_DIR / "alert_log.csv", parse_dates=["date"])
    df = df.drop_duplicates(subset=["date","kpi_key"])
    return df


def get_alert_summary() -> str:
    """Returns an overall summary of all KPI anomalies detected."""
    df = _load()
    total = len(df)
    drops  = len(df[df["direction"] == "drop"])
    spikes = len(df[df["direction"] == "spike"])
    worst  = df.loc[df["deviation"].abs().idxmax()]

    kpi_counts = df["kpi_label"].value_counts()

    lines = [f"KPI ALERT SUMMARY — {total} anomalies detected\n"]
    lines.append(f"  Drops (below normal):  {drops}")
    lines.append(f"  Spikes (above normal): {spikes}")
    lines.append(f"  Date range: {df['date'].min().date()} → {df['date'].max().date()}\n")
    lines.append("  Most frequently flagged KPIs:")
    for kpi, count in kpi_counts.items():
        lines.append(f"    {kpi:<25} {count} alerts")
    lines.append(
        f"\n  Worst anomaly: {worst['kpi_label']} on {worst['date'].date()} "
        f"— {worst['deviation']:+.1f}% (z={worst['z_score']:.2f})"
    )
    return "\n".join(lines)


def get_recent_alerts(days: int = 90) -> str:
    """Returns all KPI alerts from the last N days of data."""
    df = _load()
    cutoff = df["date"].max() - pd.Timedelta(days=days)
    recent = df[df["date"] >= cutoff].sort_values("date", ascending=False)

    if recent.empty:
        return f"No alerts found in the last {days} days of data."

    lines = [f"ALERTS — LAST {days} DAYS ({len(recent)} found)\n"]
    for _, r in recent.iterrows():
        arrow = "▼" if r["direction"] == "drop" else "▲"
        lines.append(
            f"  {r['date'].date()} | {r['kpi_label']:<25} "
            f"{arrow} {r['value']:>10,.1f}  |  {r['deviation']:+.1f}%  |  z={r['z_score']:.2f}"
        )
    return "\n".join(lines)


def get_alerts_by_kpi(kpi_name: str) -> str:
    """Returns all historical alerts for a specific KPI."""
    df = _load()
    matches = df[df["kpi_label"].str.lower().str.contains(kpi_name.lower())]

    if matches.empty:
        available = df["kpi_label"].unique().tolist()
        return f"No alerts found for '{kpi_name}'. Available KPIs: {', '.join(available)}"

    lines = [f"ALERTS FOR: {matches['kpi_label'].iloc[0]} ({len(matches)} total)\n"]
    for _, r in matches.sort_values("date").iterrows():
        arrow = "▼" if r["direction"] == "drop" else "▲"
        lines.append(
            f"  {r['date'].date()} {arrow} {r['value']:,.1f} "
            f"(expected ~{r['expected']:,.1f}, {r['deviation']:+.1f}%) — {r['message']}"
        )
    return "\n".join(lines)


def get_worst_anomaly() -> str:
    """Returns the single worst anomaly detected across all KPIs."""
    df = _load()
    worst = df.loc[df["deviation"].abs().idxmax()]
    direction = "crashed" if worst["direction"] == "drop" else "spiked"

    return (
        f"WORST ANOMALY DETECTED\n"
        f"  KPI:      {worst['kpi_label']}\n"
        f"  Date:     {worst['date'].date()}\n"
        f"  Value:    {worst['value']:,.1f}\n"
        f"  Expected: ~{worst['expected']:,.1f}\n"
        f"  Deviation:{worst['deviation']:+.1f}%\n"
        f"  Z-score:  {worst['z_score']:.2f}\n"
        f"  Summary:  {worst['kpi_label']} {direction} {abs(worst['deviation']):.1f}% "
        f"below its 14-day average on {worst['date'].date()}"
    )
