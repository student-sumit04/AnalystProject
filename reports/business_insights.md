# Business Insights Report

## Executive Summary

The synthetic fashion ecommerce business generated 59,688 sessions, 3,272 orders, and Rs 5,182,632 revenue across the analysis window. Overall visit-to-purchase conversion is 5.48% with AOV of Rs 1,584.

## Key Findings

1. The largest funnel leak is checkout-to-purchase, where only 36.44% of checkout sessions convert.
2. `Women Ethnic` contributes the highest revenue at Rs 1,732,646.
3. `Footwear` has the weakest category conversion at 4.31%.
4. The free-shipping nudge improved conversion by 17.75% versus control, with p-value 0.0000.
5. Root-cause analysis flags `Footwear` in `Mumbai` via `Influencer` as the weakest large segment, with an estimated 8 lost orders versus average conversion.

## Recommendations

1. Prioritize checkout friction analysis: payment failures, delivery promise clarity, coupon failure, and return-policy visibility.
2. Scale the free-shipping nudge if margin impact remains acceptable, because the experiment shows positive conversion lift.
3. Create a focused recovery pod for low-performing category-city-channel combinations.
4. Monitor cohort retention monthly and add CRM nudges for customers whose second purchase has not happened within 30 days.
5. Use the SQL templates in `sql/business_analysis_queries.sql` for weekly business reviews and ad hoc category diagnostics.

## Interview Positioning

This project can be explained as a productized analytics framework: it starts from raw events, builds reusable metrics, finds business risks, validates an experiment statistically, and produces a dashboard/report for decision makers.
