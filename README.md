# Sales Intelligence App

A three-tab Streamlit application for uploading opportunities, exploring them interactively, and making sales decisions from an executive dashboard.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Upload a CSV with the required opportunity columns shown in the ingestion tab, or begin with the included sample data. The dashboard obtains the USD→INR reference rate from the [Frankfurter API](https://frankfurter.dev/) and uses a clearly labelled fallback rate if the service is unavailable.
