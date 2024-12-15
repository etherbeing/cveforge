import os
import subprocess

def build(target, output_dir="dist"):
    cmd = [
        "nuitka",
        "--onefile",
        "--follow-imports",
        f"--output-dir={output_dir}",
        target
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    target_file = "main.py"
    build(target_file)
