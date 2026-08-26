# Safe Modifications

These changes are safe for students because they are small, visible, and testable.

## Config Changes

- Change `trip_count` in `generation_rules.json`.
- Change `on_time_threshold_sec` in `kpi_config.json`.
- Change `passing_score` in `validation_rules.json`.
- Add a new scenario in `scenarios.json`.

## Backend Changes

- Add one KPI in `analysis.py`.
- Add one validation check in `validation.py`.
- Adjust confidence logic in `scenarios.py`.

## Frontend Changes

- Improve one explanation card.
- Add one new KPI card.
- Add one warning state.
- Add one evidence checklist item.

After any change, run:

```bash
python scripts/generate_sample_data.py
python -m pytest
cd frontend
npm run build
```

