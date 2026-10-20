# 20-Minute Demo Script

## 0:00–2:00 — Problem and motivation
Explain that diabetes management is often reactive and that a digital twin concept aims to combine historical context with changing physiological signals. State clearly that this demo is synthetic and is not a clinical tool.

## 2:00–4:00 — Challenge alignment
Show the two data streams:
- Historical EHR-like profile: HbA1c, age, duration, adherence proxy, hypertension flag.
- Dynamic wearable-style series: simulated glucose, heart rate, HRV, sleep, steps.
Explain the two-hour glucose-spike risk target as a simulation outcome.

## 4:00–7:00 — Architecture
Walk through the architecture diagram: data generator → feature engineering → Random Forest → FastAPI → React dashboard. Mention reproducibility, modular design, and local-first setup.

## 7:00–10:00 — Data and privacy
Open generated CSVs. Show that patient IDs are synthetic and that no real patient data is bundled. Explain that any future real dataset must be licensed, de-identified, and handled under applicable privacy rules.

## 10:00–14:00 — Dashboard walkthrough
Select a synthetic patient. Review latest glucose, heart rate, sleep, steps, glucose timeline, HbA1c, adherence proxy, and hypertension history. Point out that the UI presents a virtual-patient snapshot rather than a complete human physiology simulation.

## 14:00–17:00 — Live prediction
Change the carbohydrate scenario and stress input. Run the model. Explain the probability as a model score on synthetic labels, not an individual’s real medical risk. Show the factor snapshot returned by the API.

## 17:00–19:00 — Evaluation and limitations
Show synthetic holdout metrics. Discuss leakage risk from random example splitting, synthetic-label bias, lack of external validation, and the work required before clinical use.

## 19:00–20:00 — Conclusion
Summarize what works end-to-end and next steps: patient-level temporal split, real licensed dataset evaluation, uncertainty, calibration, explainability, clinician feedback, security, and regulatory review.

## Backup plan
If internet or browser issues occur, use the local dashboard and `/docs` page. Keep screenshots of the running app and terminal output, but do not fabricate results or claim clinical validation.
