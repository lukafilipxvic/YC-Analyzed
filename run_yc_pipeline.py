from datetime import datetime, timedelta
import subprocess
import os

current_date = datetime.now()
os.makedirs(f'data/{current_date}', exist_ok=True)

pipeline_steps = [
    f"python src/get_yc_urls.py --date {current_date}",
    f"python src/get_yc_data.py --date {current_date}",
    f"python src/generate_statistics.py --date {current_date}",
    f"python src/generate_charts.py --date {current_date}"
]

def run_pipeline_steps(steps):
    for step in steps:
        result = subprocess.run(step, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Step succeeded: {step}")
            print("Output:", result.stdout)
        else:
            print(f"Step failed: {step}")
            print("Error:", result.stderr)
            break

if __name__=="__main__":
    run_pipeline_steps(pipeline_steps)