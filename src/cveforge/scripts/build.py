import subprocess


def build(target: str, output_dir: str = "dist"):
    cmd = [
        "nuitka",
        "--onefile",
        "--follow-imports",
        f"--output-dir={output_dir}",
        target,
    ]
    subprocess.run(cmd)
