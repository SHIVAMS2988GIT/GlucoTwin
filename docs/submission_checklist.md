# Submission Checklist

Fill in before submission:
- Team name: GlucoTwin
- Team leader: [Your full name]
- Team size: 1
- College / incubator: [Your institution / incubator]
- Project title: GlucoTwin — Synthetic Digital Twin for Glucose-Spike Risk
- Problem statement: combine historical EHR-like data and dynamic wearable-style signals to estimate a synthetic two-hour glucose-spike event.
- Stack: Python, FastAPI, scikit-learn, pandas, NumPy, React, Vite, Recharts.
- License: MIT
- Public repository URL: [Add after creating GitHub repository]
- Demo video URL (minimum 20 minutes): [Add after recording]
- Architecture diagram PDF/PPT: [Export docs/architecture.md Mermaid diagram or recreate in slides]
- Presentation PDF/PPT: [Create using docs/presentation_outline.md]

Final verification:
- [ ] `python scripts/generate_data.py` succeeds
- [ ] `python scripts/train_model.py` succeeds
- [ ] Backend starts and `/health` returns status `ok`
- [ ] `/docs` loads and `/api/patients` returns synthetic patient list
- [ ] Frontend loads and prediction runs
- [ ] `pytest` succeeds
- [ ] README and model card reviewed
- [ ] No secrets, API keys, or real health data in repository
- [ ] GitHub repository visibility is Public
- [ ] Demo link is accessible to evaluators
