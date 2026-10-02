# Cost Structure and Channel-Wise Profitability Analysis for Multi-Channel Restaurants

## Project
SkyCity Auckland Restaurants & Bars

## Objective
Analyze profitability across In-Store, Uber Eats, DoorDash and Self Delivery channels, quantify commission and delivery cost impact, and provide an interactive Streamlit dashboard with what-if analysis.

## Dataset
`data/SkyCity Auckland Restaurants & Bars.csv`

The dataset contains 1,696 restaurant-month records and 30 fields.

## Main KPIs
- Net Profit per Order
- Channel Margin (%)
- Commission Drag
- Self-Delivery ROI
- Profit Volatility

## Run locally

1. Install Python 3.10+.
2. Open a terminal in this project folder.
3. Run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

4. Open the local URL shown by Streamlit.

## GitHub
Upload the complete project folder to a public GitHub repository.

## Deployment
Deploy `app.py` using Streamlit Community Cloud and select the GitHub repository.

## Files
- `app.py` = Streamlit dashboard
- `analysis.py` = validation and KPI analysis
- `data/` = original dataset
- `research_paper.docx` = project report
- `executive_summary.docx` = short stakeholder summary
- `requirements.txt` = Python packages

## Important
This is an academic analytics project. The what-if section is a scenario tool and should not be treated as an audited financial forecast.
