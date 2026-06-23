"""
Pricing Intelligence Tools
Queries the ML pricing recommendations from Project 3.
"""
import pandas as pd
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def _load(objective: str = "margin"):
    df = pd.read_csv(DATA_DIR / "pricing_recommendations.csv")
    return df[df["objective"] == objective]


def get_pricing_summary(objective: str = "margin") -> str:
    """Returns an overview of all pricing recommendations for a given objective (margin or revenue)."""
    df = _load(objective)
    raises = df[df["action"] == "RAISE"]
    lowers = df[df["action"] == "LOWER"]
    holds  = df[df["action"] == "HOLD"]
    uplift_col = f"{objective}_uplift_pct"

    return (
        f"PRICING RECOMMENDATIONS — MAXIMISE {objective.upper()}\n"
        f"  Total products:     {len(df)}\n"
        f"  RAISE prices:       {len(raises)} products\n"
        f"  LOWER prices:       {len(lowers)} products\n"
        f"  HOLD prices:        {len(holds)} products\n"
        f"  Avg {objective} uplift: +{df[uplift_col].mean():.1f}%\n"
        f"  Max {objective} uplift: +{df[uplift_col].max():.1f}% ({df.loc[df[uplift_col].idxmax(),'product_name']})\n"
        f"  Avg price change:   {df['price_change_pct'].mean():+.1f}%"
    )


def get_top_opportunities(n: int = 5, objective: str = "margin") -> str:
    """Returns the top N products with the highest pricing uplift opportunity."""
    df = _load(objective)
    uplift_col = f"{objective}_uplift_pct"
    top = df.nlargest(n, uplift_col)

    lines = [f"TOP {n} {objective.upper()} OPPORTUNITIES\n"]
    for _, r in top.iterrows():
        lines.append(
            f"  {r['product_name']:<25} ({r['category']})\n"
            f"    Current: ${r['current_price']:.2f} → Optimal: ${r['optimal_price']:.2f} "
            f"({r['price_change_pct']:+.1f}%) | "
            f"{objective.title()} uplift: +{r[uplift_col]:.1f}% | "
            f"Action: {r['action']}"
        )
    return "\n".join(lines)


def get_products_by_action(action: str, objective: str = "margin") -> str:
    """Returns all products recommended to RAISE, LOWER, or HOLD price."""
    df = _load(objective)
    action = action.upper()
    filtered = df[df["action"] == action]

    if filtered.empty:
        return f"No products with action '{action}' found for {objective} objective."

    uplift_col = f"{objective}_uplift_pct"
    lines = [f"PRODUCTS TO {action} — {objective.upper()} OBJECTIVE ({len(filtered)} products)\n"]
    for _, r in filtered.sort_values(uplift_col, ascending=False).iterrows():
        lines.append(
            f"  {r['product_name']:<25} ${r['current_price']:.2f} → ${r['optimal_price']:.2f} "
            f"({r['price_change_pct']:+.1f}%) | uplift: +{r[uplift_col]:.1f}%"
        )
    return "\n".join(lines)


def get_category_pricing_summary(objective: str = "margin") -> str:
    """Returns pricing recommendations aggregated by product category."""
    df = _load(objective)
    uplift_col = f"{objective}_uplift_pct"

    cat = df.groupby("category").agg(
        products=("product_id","count"),
        avg_price_change=("price_change_pct","mean"),
        avg_uplift=(uplift_col,"mean"),
        raise_count=("action", lambda x: (x=="RAISE").sum()),
        lower_count=("action", lambda x: (x=="LOWER").sum()),
    ).round(1).sort_values("avg_uplift", ascending=False)

    lines = [f"PRICING BY CATEGORY — {objective.upper()} OBJECTIVE\n"]
    for cat_name, r in cat.iterrows():
        lines.append(
            f"  {cat_name:<15} avg price change: {r['avg_price_change']:+.1f}% | "
            f"avg {objective} uplift: +{r['avg_uplift']:.1f}% | "
            f"raise: {int(r['raise_count'])}, lower: {int(r['lower_count'])}"
        )
    return "\n".join(lines)


def get_model_performance() -> str:
    """Returns the XGBoost demand model's performance metrics."""
    with open(DATA_DIR / "model_metrics.json") as f:
        data = json.load(f)
    m = data["model_metrics"]
    top = data["top_features"][:5]

    lines = [
        "DEMAND MODEL PERFORMANCE\n",
        f"  R²:   {m['R2']} (explains {m['R2']*100:.1f}% of demand variance)",
        f"  MAE:  {m['MAE']} units",
        f"  RMSE: {m['RMSE']} units",
        f"  MAPE: {m['MAPE']}%\n",
        "  Top demand drivers:",
    ]
    for feat in top:
        lines.append(f"    {feat['feature']:<30} importance: {feat['importance']:.3f}")
    return "\n".join(lines)
