import pandas as pd
import asyncio
import os
from datetime import datetime
from api_client import APIClient
from utils import score_answer

# parse semicolon-delimited JIRA IDs into ordered lists
CONVERTERS = {
    'interp_jira': lambda x: x.split(';') if isinstance(x, str) and x else [],
    'impl_jira':   lambda x: x.split(';') if isinstance(x, str) and x else [],
    'impl_pr':     lambda x: x.split(';') if isinstance(x, str) and x else [],
}

async def run_regression(
    input_csv: str,
    output_dir: str,
    client: APIClient,
    runs: int = 3,
    historic_dir: str = None
) -> tuple[str, pd.DataFrame]:
    # Ensure directories exist
    os.makedirs(output_dir, exist_ok=True)
    if historic_dir:
        os.makedirs(historic_dir, exist_ok=True)
        # Move existing result files into historic directory (preserve names)
        for f in os.listdir(output_dir):
            if f.startswith('result_') and f.endswith('.csv'):
                os.rename(
                    os.path.join(output_dir, f),
                    os.path.join(historic_dir, f)
                )

    # Read input with converters to preserve ordered lists
    df = pd.read_csv(input_csv, converters=CONVERTERS)
    results = []

    for run_id in range(1, runs + 1):
        for _, row in df.iterrows():
            # Call the API and unpack
            resp = await client.call(row.question, row.mode)
            ans = resp.get("answer", "")
            score, passed = score_answer(ans, row.expected_answer)

            results.append({
                "run": run_id,
                "scenario": row.scenario,
                "question": row.question,
                "mode": row.mode,
                "answer": ans,
                "expected_answer": row.expected_answer,
                "interp_jira": resp.get("interp_jira", []),
                "expected_interp_jira": row.interp_jira,
                "impl_jira": resp.get("impl_jira", []),
                "expected_impl_jira": row.impl_jira,
                "impl_pr": resp.get("impl_pr", []),
                "expected_impl_pr": row.impl_pr,
                "score": score,
                "pass": passed,
            })

    # Build DataFrame
    out_df = pd.DataFrame(results)

    # Flatten list columns to semicolon-delimited strings for CSV
    list_cols = [
        'interp_jira', 'expected_interp_jira',
        'impl_jira', 'expected_impl_jira',
        'impl_pr', 'expected_impl_pr'
    ]
    for col in list_cols:
        out_df[col] = out_df[col].apply(lambda lst: ';'.join(lst))

    # Save output with timestamp
    timestamp = datetime.now().strftime("%d%m%Y_%H%M")
    out_file = os.path.join(output_dir, f"result_{timestamp}.csv")
    out_df.to_csv(out_file, index=False)
    return out_file, out_df