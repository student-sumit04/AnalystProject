# Fashion Ecommerce Funnel and Retention Analytics

This project is a business analyst case study for a fashion ecommerce platform. I built it to show how an analyst can move from raw user activity to clear business recommendations using Python, SQL, and a simple dashboard.

The main question behind the project is:

> Traffic is healthy, but where are customers dropping off, which segments need attention, and should the business scale a free-shipping nudge?

The project creates synthetic ecommerce data, calculates funnel and retention metrics, runs an A/B test analysis, stores the data in SQLite, and produces a browser dashboard plus a written business report.

## Business Context

Imagine the business team is reviewing weekly ecommerce performance. Sessions are coming in from different channels, but conversion is uneven across categories, cities, and customer groups. The team needs to know:

- How many users move from visit to product view, cart, checkout, and purchase.
- Which categories and cities are underperforming.
- Whether a free-shipping message improves conversion.
- How customer retention looks across monthly cohorts.
- What actions should be discussed in the next business review.

This project is designed around that workflow.

## Quick Start

Open PowerShell in the folder where you downloaded or cloned the project:

```powershell
cd fashion-ecommerce-funnel-retention-analytics
```

Run the complete project:

```powershell
python src\generate_project.py
```

Open the dashboard:

```powershell
start dashboard\dashboard.html
```

Or use the Windows shortcut script:

```powershell
.\run_project.bat
```

The batch file regenerates the outputs and opens the dashboard automatically.

## Requirements

- Python 3 installed on your system.
- No extra libraries are needed.
- The project uses only built-in Python modules such as `csv`, `json`, `sqlite3`, `statistics`, and `pathlib`.

If the script says it cannot update a file, close any open CSV, dashboard, report, or SQLite file and run it again.

## What The Script Does

When you run `src/generate_project.py`, it performs the full workflow:

1. Creates synthetic customer, event, and order data.
2. Saves the data as CSV files.
3. Builds a SQLite database for SQL analysis.
4. Calculates KPIs such as sessions, orders, revenue, conversion rate, and AOV.
5. Builds funnel, category, city, channel, A/B test, and cohort metrics.
6. Writes a business insight report.
7. Updates the local HTML dashboard.

## Project Structure

```text
fashion-ecommerce-funnel-retention-analytics/
  data/                         Generated CSV files and SQLite database
  dashboard/                    Local browser dashboard
  reports/                      Business report and metrics JSON
  sql/                          Reusable SQL queries for analysis
  src/                          Python automation script
  run_project.bat               One-command Windows runner
```

## Important Files

- `src/generate_project.py` - main Python file that creates data, metrics, report, database, and dashboard.
- `dashboard/dashboard.html` - dashboard that opens directly in a browser.
- `reports/business_insights.md` - written summary of findings and recommendations.
- `reports/metrics.json` - calculated metrics used by the dashboard.
- `sql/business_analysis_queries.sql` - SQL queries for funnel, retention, category, and experiment analysis.
- `data/ecommerce_analytics.sqlite` - SQLite database created from the generated data.
- `data/events.csv` - event-level user journey data.
- `data/orders.csv` - order-level transaction data.
- `data/customers.csv` - customer profile data.

## Analysis Covered

This project includes:

- Funnel conversion analysis from visit to purchase.
- Category performance comparison.
- City and channel performance review.
- Root-cause watchlist for weak city-channel-category combinations.
- Free-shipping A/B test summary with conversion lift and p-value.
- Monthly retention cohort table.
- Revenue, order, conversion, and AOV reporting.

## Dashboard Sections

The dashboard includes:

- KPI cards for sessions, orders, revenue, conversion rate, AOV, and customers.
- Funnel conversion bars.
- Daily revenue trend.
- Category performance table.
- A/B test comparison.
- Root-cause watchlist.
- Retention cohort table.

It is a static HTML dashboard, so it does not need a server. You can open it directly in your browser.

## How I Would Explain This Project

I built this project as a small but complete ecommerce analytics workflow. Instead of only showing final charts, I started by generating raw event-level and order-level data. From there, I calculated funnel movement, business KPIs, category performance, retention cohorts, and an A/B test result.

The business value is that the analysis does not stop at numbers. It points to decisions: where checkout may need improvement, which segments need deeper investigation, and whether the free-shipping nudge is worth scaling after checking margin impact.

## Interview Talking Points

- The project shows both technical and business thinking.
- Python is used for automation, not just one-time analysis.
- SQL queries are included because analysts often need to answer ad hoc business questions.
- The A/B test is interpreted in a business context, not only as a statistical output.
- The dashboard and report are built for a weekly business review style discussion.

## Data Note

All data in this project is synthetic. It is created for learning and portfolio use only. It does not contain real company data or any customer information.
