# LLM Regression Evaluation Tool

**Overview:**
A Streamlit app to run automated regression tests against an LLM API, score responses, and track historic trends.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Put your `input.csv` in `data/input/` with semicolon-delimited JIRA columns.
2. Optionally drop prior `result_*.csv` files into `data/historic/`.
3. Run:
   ```bash
   streamlit run app.py
   ```
4. In the sidebar, set your API endpoint and calls-per-minute throttle.
5. Click **Run Evaluation**.

- Outputs: `data/output/result_DDMMYYYY_HHMM.csv`.
- Historic trends plotted from files in `data/historic/`.
