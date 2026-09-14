# Project Plan

## Project Idea

Build a business analyst project for a fashion ecommerce platform that diagnoses funnel conversion, customer retention, and the impact of a free-shipping experiment.

## JD Mapping

| JD Requirement | Project Evidence |
| --- | --- |
| Structured, productized analytics frameworks | Repeatable Python pipeline generates data, metrics, report, and dashboard |
| Root-cause and deep-dive analysis | Weak segment watchlist by city, channel, and category |
| Reporting system and weekly forums | `business_insights.md` and `dashboard.html` |
| Dashboards and templates | Static dashboard plus reusable SQL query pack |
| Ad hoc data extraction | SQL templates for funnel, category, retention, and experiment analysis |
| Product performance metrics | Conversion, AOV, revenue, category performance, daily trend |
| Python automation | `src/generate_project.py` |
| Statistics, A/B testing | Two-proportion z-test for free-shipping nudge |
| Ecommerce funnels and retention | Funnel steps and monthly cohort table |

## Development Steps

1. Read the JD and identify analyst capabilities to demonstrate.
2. Create a clean project folder and subfolders.
3. Generate realistic synthetic ecommerce data.
4. Calculate funnel, revenue, retention, and experiment metrics.
5. Create SQL templates for common business analyst questions.
6. Produce an executive report for interview storytelling.
7. Build a dashboard that can be opened locally in a browser.

## Recommended Interview Story

"I designed this as a productized analytics framework for a fashion ecommerce team. The business problem is that traffic is healthy but conversion and repeat purchase are uneven. I built a Python pipeline to generate and analyze event-level data, wrote SQL templates for ad hoc analysis, evaluated a free-shipping experiment statistically, and created a dashboard/report for weekly business review. The final recommendation is to scale the free-shipping nudge after checking margins, while separately fixing checkout friction and low-performing city-channel-category pockets."
