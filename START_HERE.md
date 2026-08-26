# Start Here

## اليوم الأول

افتح هذا المستودع كمنتج تدريبي كامل، وليس كملفات متفرقة. هدفك أن تفهم الرحلة ثم تشغلها ثم تعدل جزءًا صغيرًا وتوثق الدليل.

## Step 1 - Understand

Read these files:

- `README.md`
- `docs/LEARNING_PATH.md`
- `workbook/slice-01-overview.md`

Then open the frontend and visit:

- `Repo Canvas`
- `Repo Structure`

## Step 2 - Run The Data Journey

```bash
pip install -r requirements.txt
python scripts/generate_sample_data.py
python -m pytest
```

This creates generated route data, validates it, analyzes it, runs scenarios, and produces a recommendation.

## Step 3 - Run The API

```bash
uvicorn backend.main:app --reload
```

Open:

- `http://127.0.0.1:8000/api/project`
- `http://127.0.0.1:8000/api/kpis`
- `http://127.0.0.1:8000/api/recommendation`

## Step 4 - Run The Frontend

```bash
cd frontend
npm install
npm run dev
```

## Step 5 - Capture Evidence

For every completed task, capture:

- screenshot
- changed files
- test result
- generated output
- short explanation
- commit link when available

