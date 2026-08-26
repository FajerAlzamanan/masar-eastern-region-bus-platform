# Slice 02 - Data Model

## Purpose

Show how bus operations become tables. Students should understand `routes`, `stops`, `trips`, and `stop_events`.

## Files

- `config/generation_rules.json`
- `backend/generator.py`
- `frontend/src/App.jsx`

## Done Means

- Data Model page explains relationships.
- Data Model page shows an ERD for `routes`, `stops`, `trips`, and `stop_events`.
- Student can click a table and inspect live preview rows from `/api/tables/{table_name}`.
- Generated CSV files match the model.
- Student can explain why `stop_events` is the analysis table.

## Evidence To Capture

- Screenshot of the ERD with `stop_events` selected.
- Screenshot of the live preview table.
- Short explanation of one field-to-decision connection, for example `added_delay_sec` feeding delay ranking or `delay_cause` feeding the cause chart.
