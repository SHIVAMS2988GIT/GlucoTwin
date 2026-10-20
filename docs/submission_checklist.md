# Submission Checklist

Fill in before submission:
- Team name: GlucoTwin
- Team leader: Shivam Mishra
- Team size: 1
- College / incubator: Birla Institute of technology Mesra
- Project title: GlucoTwin — Synthetic Digital Twin for Glucose-Spike Risk
- Problem statement: combine historical EHR-like data and dynamic wearable-style signals to estimate a synthetic two-hour glucose-spike event.
- Stack: Python, FastAPI, scikit-learn, pandas, NumPy, React, Vite, Recharts.
- License: MIT
- Public repository URL: https://github.com/SHIVAMS2988GIT/GlucoTwin
- Architecture diagram PDF/PPT: https://drive.google.com/file/d/1ekLdJ2oZYooRwLFXU_SP1UiwMrhVG7tn/view?usp=sharing
- Presentation PDF/PPT: https://docs.google.com/presentation/d/1NMObQB8c5n_E74r4vbsswG3W6U4_ANN1/edit?usp=sharing&ouid=106220844458152638865&rtpof=true&sd=true

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
