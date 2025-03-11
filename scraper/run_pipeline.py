from datetime import datetime
import subprocess
import os
from pathlib import Path

current_date = datetime.now().strftime('%Y-%m-%d')
# Create path reference to the data directory in parent folder
data_dir = Path(__file__).resolve().parent.parent / "data" / current_date
os.makedirs(data_dir, exist_ok=True)

pipeline_steps = [
    f"uv run python -u src/get_yc_urls.py --date {current_date}",
    f"uv run python -u src/get_yc_data.py --date {current_date}",
    #f"uv run python src/generate_statistics.py --date {current_date}",
    #f"uv run python src/generate_charts.py --date {current_date}",
]

def run_pipeline_steps(steps):
    for step in steps:
        result = subprocess.run(step, shell=True)
        if result.returncode == 0:
            print(f"Step succeeded: {step}")
            print("Output:", result.stdout)
        else:
            print(f"Step failed: {step}")
            print("Error:", result.stderr)
            break

if __name__=="__main__":
    run_pipeline_steps(pipeline_steps)