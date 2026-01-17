import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_name):
    print(f"RUN {script_name}")

    result = subprocess.run(
        [sys.executable, script_name],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(f"STDOUT_{script_name}")
        print(result.stdout.strip())

    if result.returncode != 0:
        print(f"STDERR_{script_name}")
        print(result.stderr.strip())
        raise RuntimeError(f"SCRIPT_FAILED {script_name}")

    print(f"DONE {script_name}")

def main():
    print("PIPELINE_START")

    run_script("collecting_news.py")
    run_script("clean_data.py")
    run_script("sentiment_analysis.py")

    print("PIPELINE_DONE")

if __name__ == "__main__":
    main()