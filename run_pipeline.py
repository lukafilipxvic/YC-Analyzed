from datetime import datetime
import subprocess
import os

current_date = datetime.now().strftime('%Y-%m-%d')
os.makedirs(f'data/{current_date}', exist_ok=True)

pipeline_steps = [
    f"uv run python -u src/get_yc_urls.py --date {current_date}",
    f"uv run python -u src/get_yc_data.py --date {current_date}",
    f"uv run python src/generate_statistics.py --date {current_date}",
    f"uv run python src/generate_charts.py --date {current_date}",
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