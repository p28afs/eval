import streamlit as st
import nest_asyncio
nest_asyncio.apply()  # allow nested asyncio loops in Streamlit

import pandas as pd
import glob
import asyncio
import matplotlib.pyplot as plt
from regression import run_regression, CONVERTERS
from api_client import APIClient

# Icons for pass/fail
PASS_ICON = "✔"
FAIL_ICON = "✖"

st.title("LLM Regression Evaluation Tool")

# --- Sidebar Configuration ---
BASE_URL     = st.sidebar.text_input("API Base URL", "http://localhost:8000")
CALLS_PER_MIN = st.sidebar.number_input("Calls per minute", min_value=1, max_value=100, value=20)

INPUT_CSV  = "data/input/input.csv"
OUTPUT_DIR = "data/output"
HIST_DIR   = "data/historic"

if st.button("Run Evaluation"):
    status = st.empty()
    client = APIClient(BASE_URL, calls_per_minute=CALLS_PER_MIN)

    async def evaluate():
        # Run regression and archive old results
        out_file, df = await run_regression(
            INPUT_CSV, OUTPUT_DIR, client,
            runs=3, historic_dir=HIST_DIR
        )
        status.text(f"Results saved to {out_file}")

        # Prepare and style results table
        df_display = df.copy()
        df_display['pass_flag'] = df_display['pass'].apply(lambda x: PASS_ICON if x else FAIL_ICON)

        def color_score(val):
            if val < 0.7:
                return 'background-color: #ff4b4b'
            elif val < 0.8:
                return 'background-color: #ffbf00'
            elif val < 0.9:
                return 'background-color: #ffff66'
            else:
                return 'background-color: #90ee90'

        def color_pass(val):
            return 'color: green' if val == PASS_ICON else 'color: red'

        styled = (
            df_display.style
            .applymap(color_score, subset=['score'])
            .applymap(color_pass, subset=['pass_flag'])
            .hide(axis='index')
        )

        # Display styled results first
        st.subheader("Current Run Results")
        st.write(styled)

        # Prepare historic data if available
        hist_files = glob.glob(f"{HIST_DIR}/result_*.csv")
        hist = pd.DataFrame()
        if hist_files:
            hist = pd.concat([pd.read_csv(f, converters=CONVERTERS) for f in hist_files], ignore_index=True)

        # 2x2 grid for charts
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Average Score by Scenario")
            st.bar_chart(df.groupby("scenario")["score"].mean())
        with col2:
            if not hist.empty:
                score_trend = hist.groupby('run')['score'].mean().reset_index()
                score_trend['run'] = score_trend['run'].astype(str)
                st.subheader("Historic Avg Score by Run")
                st.line_chart(score_trend.set_index('run')['score'])

        col3, col4 = st.columns(2)
        with col3:
            if not hist.empty:
                pass_counts = hist.groupby('run')['pass'].sum()
                total_counts = hist.groupby('run')['pass'].count()
                pass_ratio = (pass_counts / total_counts).reset_index().rename(columns={'pass':'pass_ratio'})
                pass_ratio['run'] = pass_ratio['run'].astype(str)
                st.subheader("Historic Pass Ratio by Run")
                st.line_chart(pass_ratio.set_index('run')['pass_ratio'])
        with col4:
            if not hist.empty:
                st.subheader("Scenario Quadrant Analysis")
                scenario_stats = hist.groupby('scenario').agg(
                    avg_score=('score','mean'),
                    pass_rate=('pass','mean')
                ).reset_index()
                thresh_score, thresh_pass = 0.8, 0.8
                fig, ax = plt.subplots()
                ax.scatter(scenario_stats['avg_score'], scenario_stats['pass_rate'], s=100)
                for _, row in scenario_stats.iterrows():
                    ax.annotate(str(row['scenario']), (row['avg_score'], row['pass_rate']))
                ax.axvline(thresh_score, color='black', linestyle='--')
                ax.axhline(thresh_pass, color='black', linestyle='--')
                ax.set_xlabel('Average Score')
                ax.set_ylabel('Pass Rate')
                ax.set_xlim(0,1)
                ax.set_ylim(0,1)
                st.pyplot(fig)

    asyncio.run(evaluate())