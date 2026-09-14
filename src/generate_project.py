from __future__ import annotations

import csv
import json
import math
import random
import sqlite3
import statistics
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
DASHBOARD_DIR = ROOT / "dashboard"
RANDOM_SEED = 42


CATEGORIES = {
    "Women Ethnic": {"aov": 1850, "base": 0.052},
    "Men Casual": {"aov": 1650, "base": 0.046},
    "Beauty": {"aov": 950, "base": 0.061},
    "Footwear": {"aov": 2200, "base": 0.039},
    "Kids": {"aov": 1200, "base": 0.043},
}

CITY_EFFECT = {
    "Bengaluru": 0.006,
    "Delhi NCR": 0.002,
    "Mumbai": 0.001,
    "Hyderabad": -0.001,
    "Pune": 0.000,
    "Jaipur": -0.004,
    "Lucknow": -0.006,
    "Indore": -0.005,
}

CHANNEL_EFFECT = {
    "Organic": 0.004,
    "Paid Search": -0.001,
    "Influencer": 0.002,
    "Push": 0.005,
    "Affiliate": -0.004,
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def choose_weighted(options: list[tuple[str, float]]) -> str:
    total = sum(weight for _, weight in options)
    pick = random.uniform(0, total)
    upto = 0.0
    for value, weight in options:
        upto += weight
        if upto >= pick:
            return value
    return options[-1][0]


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_sqlite(path: Path, tables: dict[str, list[dict]]) -> None:
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    try:
        for table_name, rows in tables.items():
            columns = list(rows[0].keys())
            column_defs = ", ".join(f"{column} TEXT" for column in columns)
            connection.execute(f"CREATE TABLE {table_name} ({column_defs})")
            placeholders = ", ".join("?" for _ in columns)
            connection.executemany(
                f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
                [[row[column] for column in columns] for row in rows],
            )
        connection.commit()
    finally:
        connection.close()


def generate_data() -> tuple[list[dict], list[dict], list[dict]]:
    random.seed(RANDOM_SEED)
    start = date(2026, 1, 1)
    days = 180
    customer_count = 5200

    customers = []
    for customer_num in range(1, customer_count + 1):
        acquired = start + timedelta(days=random.randint(0, days - 1))
        city = choose_weighted([
            ("Bengaluru", 19), ("Delhi NCR", 18), ("Mumbai", 16), ("Hyderabad", 13),
            ("Pune", 10), ("Jaipur", 8), ("Lucknow", 8), ("Indore", 8),
        ])
        segment = choose_weighted([("New", 42), ("Occasional", 35), ("Loyal", 18), ("High Value", 5)])
        customers.append({
            "customer_id": f"C{customer_num:05d}",
            "acquired_date": acquired.isoformat(),
            "city": city,
            "segment": segment,
        })

    events = []
    orders = []
    session_num = 1
    order_num = 1

    for day_index in range(days):
        current = start + timedelta(days=day_index)
        weekday_lift = 1.18 if current.weekday() >= 4 else 1.0
        sale_lift = 1.55 if 72 <= day_index <= 90 else 1.0
        traffic = int(random.gauss(290 * weekday_lift * sale_lift, 32))

        for _ in range(max(170, traffic)):
            customer = random.choice(customers)
            category = choose_weighted([
                ("Women Ethnic", 27), ("Men Casual", 25), ("Beauty", 17),
                ("Footwear", 18), ("Kids", 13),
            ])
            channel = choose_weighted([
                ("Organic", 31), ("Paid Search", 26), ("Influencer", 16),
                ("Push", 14), ("Affiliate", 13),
            ])
            device = choose_weighted([("Android", 68), ("iOS", 24), ("Web", 8)])
            experiment = choose_weighted([("control", 50), ("free_shipping_nudge", 50)])
            city = customer["city"]
            session_id = f"S{session_num:07d}"
            session_num += 1

            base_conversion = CATEGORIES[category]["base"] + CITY_EFFECT[city] + CHANNEL_EFFECT[channel]
            if experiment == "free_shipping_nudge":
                base_conversion += 0.006
            if customer["segment"] in {"Loyal", "High Value"}:
                base_conversion += 0.009
            if 112 <= day_index <= 130 and category == "Footwear":
                base_conversion -= 0.018
            if 112 <= day_index <= 130 and city in {"Lucknow", "Indore", "Jaipur"}:
                base_conversion -= 0.006

            purchase_prob = clamp(base_conversion, 0.012, 0.095)
            view_prob = clamp(0.79 + (purchase_prob * 0.9), 0.68, 0.91)
            cart_prob = clamp(0.21 + (purchase_prob * 1.7), 0.13, 0.36)
            checkout_prob = clamp(0.52 + (purchase_prob * 1.2), 0.42, 0.72)

            base_event = {
                "event_date": current.isoformat(),
                "session_id": session_id,
                "customer_id": customer["customer_id"],
                "city": city,
                "segment": customer["segment"],
                "channel": channel,
                "device": device,
                "category": category,
                "experiment_group": experiment,
                "revenue": 0,
            }
            events.append({**base_event, "event_type": "visit"})

            if random.random() <= view_prob:
                events.append({**base_event, "event_type": "product_view"})
                if random.random() <= cart_prob:
                    events.append({**base_event, "event_type": "add_to_cart"})
                    if random.random() <= checkout_prob:
                        events.append({**base_event, "event_type": "checkout_start"})
                        if random.random() <= purchase_prob / (view_prob * cart_prob * checkout_prob):
                            revenue = max(250, round(random.gauss(CATEGORIES[category]["aov"], CATEGORIES[category]["aov"] * 0.28)))
                            discount = random.choice([0, 5, 10, 15, 20, 25, 30])
                            delivery_days = random.choice([1, 2, 3, 4, 5, 6])
                            events.append({**base_event, "event_type": "purchase", "revenue": revenue})
                            orders.append({
                                "order_id": f"O{order_num:06d}",
                                "order_date": current.isoformat(),
                                "session_id": session_id,
                                "customer_id": customer["customer_id"],
                                "city": city,
                                "category": category,
                                "channel": channel,
                                "experiment_group": experiment,
                                "order_value": revenue,
                                "discount_pct": discount,
                                "delivery_days": delivery_days,
                            })
                            order_num += 1

    return customers, events, orders


def proportion_z_test(success_a: int, total_a: int, success_b: int, total_b: int) -> dict:
    p1 = success_a / total_a
    p2 = success_b / total_b
    pooled = (success_a + success_b) / (total_a + total_b)
    se = math.sqrt(pooled * (1 - pooled) * ((1 / total_a) + (1 / total_b)))
    z = (p2 - p1) / se if se else 0
    p_value = math.erfc(abs(z) / math.sqrt(2))
    return {"control_rate": p1, "test_rate": p2, "lift": (p2 / p1) - 1, "z_score": z, "p_value": p_value}


def analyze(customers: list[dict], events: list[dict], orders: list[dict]) -> dict:
    sessions = {event["session_id"]: event for event in events if event["event_type"] == "visit"}
    funnel_counts = {
        step: len({event["session_id"] for event in events if event["event_type"] == step})
        for step in ["visit", "product_view", "add_to_cart", "checkout_start", "purchase"]
    }
    rates = {
        "visit_to_view": funnel_counts["product_view"] / funnel_counts["visit"],
        "view_to_cart": funnel_counts["add_to_cart"] / funnel_counts["product_view"],
        "cart_to_checkout": funnel_counts["checkout_start"] / funnel_counts["add_to_cart"],
        "checkout_to_purchase": funnel_counts["purchase"] / funnel_counts["checkout_start"],
        "visit_to_purchase": funnel_counts["purchase"] / funnel_counts["visit"],
    }

    def grouped_conversion(key: str) -> list[dict]:
        groups = defaultdict(lambda: {"sessions": set(), "purchases": set(), "revenue": 0})
        for event in events:
            group = groups[event[key]]
            group["sessions"].add(event["session_id"])
            if event["event_type"] == "purchase":
                group["purchases"].add(event["session_id"])
                group["revenue"] += int(event["revenue"])
        rows = []
        for name, values in groups.items():
            rows.append({
                key: name,
                "sessions": len(values["sessions"]),
                "purchases": len(values["purchases"]),
                "conversion_rate": len(values["purchases"]) / len(values["sessions"]),
                "revenue": values["revenue"],
            })
        return sorted(rows, key=lambda row: row["conversion_rate"])

    category = grouped_conversion("category")
    city = grouped_conversion("city")
    channel = grouped_conversion("channel")

    daily = defaultdict(lambda: {"sessions": set(), "purchases": set(), "revenue": 0})
    for event in events:
        bucket = daily[event["event_date"]]
        bucket["sessions"].add(event["session_id"])
        if event["event_type"] == "purchase":
            bucket["purchases"].add(event["session_id"])
            bucket["revenue"] += int(event["revenue"])
    daily_rows = []
    for day, values in sorted(daily.items()):
        daily_rows.append({
            "date": day,
            "sessions": len(values["sessions"]),
            "purchases": len(values["purchases"]),
            "conversion_rate": len(values["purchases"]) / len(values["sessions"]),
            "revenue": values["revenue"],
        })

    experiment = defaultdict(lambda: {"sessions": set(), "purchases": set(), "revenue": 0})
    for event in events:
        bucket = experiment[event["experiment_group"]]
        bucket["sessions"].add(event["session_id"])
        if event["event_type"] == "purchase":
            bucket["purchases"].add(event["session_id"])
            bucket["revenue"] += int(event["revenue"])
    ab = {
        group: {
            "sessions": len(values["sessions"]),
            "purchases": len(values["purchases"]),
            "conversion_rate": len(values["purchases"]) / len(values["sessions"]),
            "revenue": values["revenue"],
        }
        for group, values in experiment.items()
    }
    ab_test = proportion_z_test(
        ab["control"]["purchases"],
        ab["control"]["sessions"],
        ab["free_shipping_nudge"]["purchases"],
        ab["free_shipping_nudge"]["sessions"],
    )

    customer_first = {}
    customer_months = defaultdict(set)
    for order in orders:
        month = order["order_date"][:7]
        customer_id = order["customer_id"]
        customer_first[customer_id] = min(customer_first.get(customer_id, month), month)
        customer_months[customer_id].add(month)

    cohort = defaultdict(lambda: Counter())
    for customer_id, first_month in customer_first.items():
        first_date = date.fromisoformat(first_month + "-01")
        for active_month in customer_months[customer_id]:
            active_date = date.fromisoformat(active_month + "-01")
            offset = (active_date.year - first_date.year) * 12 + active_date.month - first_date.month
            if 0 <= offset <= 5:
                cohort[first_month][offset] += 1

    cohort_rows = []
    for month, counts in sorted(cohort.items()):
        base = counts[0] or 1
        row = {"cohort": month, "customers": counts[0]}
        for offset in range(0, 6):
            row[f"m{offset}"] = counts[offset] / base
        cohort_rows.append(row)

    rca = []
    combo = defaultdict(lambda: {"sessions": set(), "purchases": set()})
    for event in events:
        key = (event["city"], event["channel"], event["category"])
        combo[key]["sessions"].add(event["session_id"])
        if event["event_type"] == "purchase":
            combo[key]["purchases"].add(event["session_id"])
    overall_conversion = funnel_counts["purchase"] / funnel_counts["visit"]
    for (combo_city, combo_channel, combo_category), values in combo.items():
        sessions_count = len(values["sessions"])
        if sessions_count < 300:
            continue
        conversion = len(values["purchases"]) / sessions_count
        gap = conversion - overall_conversion
        rca.append({
            "city": combo_city,
            "channel": combo_channel,
            "category": combo_category,
            "sessions": sessions_count,
            "conversion_rate": conversion,
            "gap_vs_average": gap,
            "lost_orders_estimate": round((overall_conversion - conversion) * sessions_count) if gap < 0 else 0,
        })
    rca = sorted(rca, key=lambda row: row["gap_vs_average"])[:10]

    revenue_values = [int(order["order_value"]) for order in orders]
    return {
        "kpis": {
            "sessions": funnel_counts["visit"],
            "orders": len(orders),
            "revenue": sum(revenue_values),
            "conversion_rate": rates["visit_to_purchase"],
            "aov": statistics.mean(revenue_values),
            "customers": len(customers),
        },
        "funnel_counts": funnel_counts,
        "funnel_rates": rates,
        "category": category,
        "city": city,
        "channel": channel,
        "daily": daily_rows,
        "ab_summary": ab,
        "ab_test": ab_test,
        "cohort": cohort_rows,
        "root_cause": rca,
    }


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def inr(value: float) -> str:
    return f"Rs {value:,.0f}"


def write_report(metrics: dict) -> None:
    weakest = metrics["root_cause"][0]
    best_category = max(metrics["category"], key=lambda row: row["revenue"])
    worst_category = min(metrics["category"], key=lambda row: row["conversion_rate"])
    ab = metrics["ab_test"]
    content = f"""# Business Insights Report

## Executive Summary

The synthetic fashion ecommerce business generated {metrics["kpis"]["sessions"]:,} sessions, {metrics["kpis"]["orders"]:,} orders, and {inr(metrics["kpis"]["revenue"])} revenue across the analysis window. Overall visit-to-purchase conversion is {pct(metrics["kpis"]["conversion_rate"])} with AOV of {inr(metrics["kpis"]["aov"])}.

## Key Findings

1. The largest funnel leak is checkout-to-purchase, where only {pct(metrics["funnel_rates"]["checkout_to_purchase"])} of checkout sessions convert.
2. `{best_category["category"]}` contributes the highest revenue at {inr(best_category["revenue"])}.
3. `{worst_category["category"]}` has the weakest category conversion at {pct(worst_category["conversion_rate"])}.
4. The free-shipping nudge improved conversion by {pct(ab["lift"])} versus control, with p-value {ab["p_value"]:.4f}.
5. Root-cause analysis flags `{weakest["category"]}` in `{weakest["city"]}` via `{weakest["channel"]}` as the weakest large segment, with an estimated {weakest["lost_orders_estimate"]} lost orders versus average conversion.

## Recommendations

1. Prioritize checkout friction analysis: payment failures, delivery promise clarity, coupon failure, and return-policy visibility.
2. Scale the free-shipping nudge if margin impact remains acceptable, because the experiment shows positive conversion lift.
3. Create a focused recovery pod for low-performing category-city-channel combinations.
4. Monitor cohort retention monthly and add CRM nudges for customers whose second purchase has not happened within 30 days.
5. Use the SQL templates in `sql/business_analysis_queries.sql` for weekly business reviews and ad hoc category diagnostics.

## Interview Positioning

This project can be explained as a productized analytics framework: it starts from raw events, builds reusable metrics, finds business risks, validates an experiment statistically, and produces a dashboard/report for decision makers.
"""
    (REPORTS_DIR / "business_insights.md").write_text(content, encoding="utf-8")


def write_dashboard(metrics: dict) -> None:
    payload = json.dumps(metrics, indent=2)
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Fashion Ecommerce BA Dashboard</title>
  <style>
    :root {
      --ink: #17212b;
      --muted: #667085;
      --line: #d9dee7;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --teal: #0f766e;
      --rose: #be3455;
      --gold: #b7791f;
      --blue: #2563eb;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--bg);
    }
    header {
      padding: 28px 36px 18px;
      background: #ffffff;
      border-bottom: 1px solid var(--line);
    }
    h1 { margin: 0; font-size: 28px; letter-spacing: 0; }
    .subtitle { margin-top: 8px; color: var(--muted); max-width: 920px; line-height: 1.5; }
    main { padding: 24px 36px 40px; }
    .grid { display: grid; gap: 16px; }
    .kpis { grid-template-columns: repeat(6, minmax(130px, 1fr)); }
    .two { grid-template-columns: 1.1fr 0.9fr; margin-top: 18px; }
    .three { grid-template-columns: repeat(3, 1fr); margin-top: 18px; }
    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }
    .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
    .value { font-size: 25px; font-weight: 700; margin-top: 8px; }
    .section-title { margin: 0 0 14px; font-size: 18px; }
    .bar-row { display: grid; grid-template-columns: 150px 1fr 72px; gap: 12px; align-items: center; margin: 10px 0; }
    .bar-track { height: 10px; background: #edf0f5; border-radius: 999px; overflow: hidden; }
    .bar { height: 100%; background: var(--teal); }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { border-bottom: 1px solid var(--line); padding: 9px 7px; text-align: left; }
    th { color: var(--muted); font-weight: 700; }
    .pill { display: inline-block; padding: 4px 8px; border-radius: 999px; background: #e8f5f3; color: var(--teal); font-weight: 700; }
    .warning { color: var(--rose); font-weight: 700; }
    .note { color: var(--muted); line-height: 1.45; }
    .spark { display: flex; align-items: end; gap: 2px; height: 130px; border-bottom: 1px solid var(--line); }
    .spark div { flex: 1; min-width: 2px; background: var(--blue); opacity: .8; }
    @media (max-width: 980px) {
      main, header { padding-left: 18px; padding-right: 18px; }
      .kpis, .two, .three { grid-template-columns: 1fr; }
      .bar-row { grid-template-columns: 120px 1fr 62px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Fashion Ecommerce Funnel & Retention Dashboard</h1>
    <div class="subtitle">A business analyst project built from synthetic event and order data. It tracks funnel performance, category health, experiment impact, retention cohorts, and root-cause opportunities for weekly business reviews.</div>
  </header>
  <main>
    <section class="grid kpis" id="kpis"></section>
    <section class="grid two">
      <div class="card">
        <h2 class="section-title">Funnel Conversion</h2>
        <div id="funnel"></div>
      </div>
      <div class="card">
        <h2 class="section-title">Daily Revenue Trend</h2>
        <div class="spark" id="spark"></div>
        <p class="note">The sale window increases volume, while later low-performing pockets create visible softness in conversion.</p>
      </div>
    </section>
    <section class="grid three">
      <div class="card">
        <h2 class="section-title">Category Performance</h2>
        <div id="category"></div>
      </div>
      <div class="card">
        <h2 class="section-title">A/B Test: Free Shipping</h2>
        <div id="ab"></div>
      </div>
      <div class="card">
        <h2 class="section-title">Root-Cause Watchlist</h2>
        <div id="rca"></div>
      </div>
    </section>
    <section class="card" style="margin-top:18px">
      <h2 class="section-title">Retention Cohorts</h2>
      <div id="cohort"></div>
    </section>
  </main>
  <script>
    const data = __DATA__;
    const fmtPct = value => `${(value * 100).toFixed(2)}%`;
    const fmtInr = value => `Rs ${Math.round(value).toLocaleString("en-IN")}`;
    const kpis = [
      ["Sessions", data.kpis.sessions.toLocaleString("en-IN")],
      ["Orders", data.kpis.orders.toLocaleString("en-IN")],
      ["Revenue", fmtInr(data.kpis.revenue)],
      ["Conversion", fmtPct(data.kpis.conversion_rate)],
      ["AOV", fmtInr(data.kpis.aov)],
      ["Customers", data.kpis.customers.toLocaleString("en-IN")]
    ];
    document.getElementById("kpis").innerHTML = kpis.map(([label, value]) => `<div class="card"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");

    const funnelNames = {
      visit: "Visit",
      product_view: "Product view",
      add_to_cart: "Add to cart",
      checkout_start: "Checkout",
      purchase: "Purchase"
    };
    const maxFunnel = data.funnel_counts.visit;
    document.getElementById("funnel").innerHTML = Object.entries(data.funnel_counts).map(([step, count]) => {
      const width = Math.max(2, count / maxFunnel * 100);
      return `<div class="bar-row"><strong>${funnelNames[step]}</strong><div class="bar-track"><div class="bar" style="width:${width}%"></div></div><span>${count.toLocaleString("en-IN")}</span></div>`;
    }).join("");

    const maxRevenue = Math.max(...data.daily.map(d => d.revenue));
    document.getElementById("spark").innerHTML = data.daily.map(d => `<div title="${d.date}: ${fmtInr(d.revenue)}" style="height:${Math.max(3, d.revenue / maxRevenue * 120)}px"></div>`).join("");

    document.getElementById("category").innerHTML = `<table><thead><tr><th>Category</th><th>Conv.</th><th>Revenue</th></tr></thead><tbody>${data.category.slice().sort((a,b)=>b.revenue-a.revenue).map(row => `<tr><td>${row.category}</td><td>${fmtPct(row.conversion_rate)}</td><td>${fmtInr(row.revenue)}</td></tr>`).join("")}</tbody></table>`;

    const ab = data.ab_summary;
    document.getElementById("ab").innerHTML = `
      <p><span class="pill">${fmtPct(data.ab_test.lift)} lift</span></p>
      <table><thead><tr><th>Group</th><th>Sessions</th><th>Conv.</th></tr></thead><tbody>
      ${Object.entries(ab).map(([group, row]) => `<tr><td>${group}</td><td>${row.sessions.toLocaleString("en-IN")}</td><td>${fmtPct(row.conversion_rate)}</td></tr>`).join("")}
      </tbody></table>
      <p class="note">p-value: ${data.ab_test.p_value.toFixed(4)}. Use alongside margin impact before rollout.</p>`;

    document.getElementById("rca").innerHTML = `<table><thead><tr><th>Segment</th><th>Conv.</th><th>Lost orders</th></tr></thead><tbody>${data.root_cause.slice(0,6).map(row => `<tr><td>${row.city}<br><span class="note">${row.channel}, ${row.category}</span></td><td class="warning">${fmtPct(row.conversion_rate)}</td><td>${row.lost_orders_estimate}</td></tr>`).join("")}</tbody></table>`;

    document.getElementById("cohort").innerHTML = `<table><thead><tr><th>Cohort</th><th>Customers</th><th>M0</th><th>M1</th><th>M2</th><th>M3</th><th>M4</th><th>M5</th></tr></thead><tbody>${data.cohort.map(row => `<tr><td>${row.cohort}</td><td>${row.customers}</td><td>${fmtPct(row.m0)}</td><td>${fmtPct(row.m1)}</td><td>${fmtPct(row.m2)}</td><td>${fmtPct(row.m3)}</td><td>${fmtPct(row.m4)}</td><td>${fmtPct(row.m5)}</td></tr>`).join("")}</tbody></table>`;
  </script>
</body>
</html>
"""
    html = html.replace("__DATA__", payload)
    (DASHBOARD_DIR / "dashboard.html").write_text(html, encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    DASHBOARD_DIR.mkdir(exist_ok=True)
    customers, events, orders = generate_data()
    write_csv(DATA_DIR / "customers.csv", customers)
    write_csv(DATA_DIR / "events.csv", events)
    write_csv(DATA_DIR / "orders.csv", orders)
    write_sqlite(DATA_DIR / "ecommerce_analytics.sqlite", {
        "customers": customers,
        "events": events,
        "orders": orders,
    })
    metrics = analyze(customers, events, orders)
    (REPORTS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    write_report(metrics)
    write_dashboard(metrics)
    print("Generated synthetic data, metrics, report, and dashboard.")
    print(f"Dashboard: {DASHBOARD_DIR / 'dashboard.html'}")
    print(f"Report: {REPORTS_DIR / 'business_insights.md'}")
    print(f"SQLite database: {DATA_DIR / 'ecommerce_analytics.sqlite'}")


if __name__ == "__main__":
    try:
        main()
    except PermissionError as error:
        print("Could not update one of the output files.")
        print("Close any open CSV, SQLite, report, or dashboard files, then run the project again.")
        print(f"Locked file or folder: {error.filename}")
        raise SystemExit(1)
