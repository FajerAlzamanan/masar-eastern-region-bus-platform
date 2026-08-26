# Learning Path

## الهدف

يتعلم فريق B كيف يتحول مشروع Bus Delay DSS إلى منتج برمجي كامل. لا يكفي أن يرى الطالب نتيجة نهائية؛ يجب أن يفهم كيف انتقلت الفكرة من مشكلة إلى Config ثم Python ثم API ثم UI ثم Evidence.

## The Loop

For every slice:

1. Read the slice workbook.
2. Open the related config file.
3. Run the backend function or notebook step.
4. Inspect the API response.
5. Open the frontend page.
6. Modify one small rule.
7. Run tests.
8. Capture evidence.
9. Update the report.

## Week Plan

- Week 1: problem, stakeholders, decision, repo shell, overview, data model.
- Week 2: synthetic data, validation, quality gate.
- Week 3: KPIs, dashboard, explorer, scenario comparison.
- Week 4: recommendation, audit, report, presentation, demo.

## Data Model Check

Before using the Dashboard, open the Data Model page and inspect the ERD.
Click each table and compare the preview rows with the generated CSV files.

Minimum explanation expected from the student:

- `routes` defines the route being analyzed.
- `stops` defines the stop sequence.
- `trips` defines each scheduled bus trip and final delay.
- `stop_events` is the analysis table because it connects trip, stop, passenger load, dwell time, delay, and cause.

Useful API checks:

- `GET /api/data-model`
- `GET /api/tables/routes`
- `GET /api/tables/stops`
- `GET /api/tables/trips`
- `GET /api/tables/stop_events`
