#!/usr/bin/env python3
"""
bootstrap_labs.py
Usage: python3 bootstrap_labs.py labs.txt

labs.txt: one URL (git repo or archive or github short 'user/repo') per line.
"""

import sys
import os
import subprocess
import urllib.request
import tarfile
import zipfile
import pathlib
from urllib.parse import urlparse

BASE_DIR = pathlib.Path.cwd() / "labs"
BOX_NAME = "ubuntu/focal64"  # base box used for all generated Vagrantfiles


def run(cmd, cwd=None):
    print("RUN:", cmd)
    r = subprocess.run(cmd, shell=True, text=True, cwd=cwd)
    if r.returncode != 0:
        print("Command failed:", cmd)
    return r.returncode


def clone_or_download(url, dest):
    dest.mkdir(parents=True, exist_ok=True)
    # Git repo?
    if (
        url.endswith(".git")
        or "github.com" in url
        and not url.endswith((".zip", ".tar.gz", ".tgz"))
    ):
        print("Cloning git repo:", url)
        return run(f"git clone --depth 1 {url} {dest}") == 0
    # Handle github short "user/repo"
    if "/" in url and not urlparse(url).scheme:
        url = "https://github.com/" + url
    # If URL points to archive
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    tmpfile = dest / filename
    try:
        print("Downloading:", url)
        urllib.request.urlretrieve(url, tmpfile)
    except Exception as e:
        print("Download error:", e)
        return False
    # Extract if archive
    try:
        if filename.endswith((".tar.gz", ".tgz")):
            with tarfile.open(tmpfile, "r:gz") as tf:
                tf.extractall(path=dest)
            tmpfile.unlink()
            return True
        if filename.endswith(".zip"):
            with zipfile.ZipFile(tmpfile, "r") as zf:
                zf.extractall(path=dest)
            tmpfile.unlink()
            return True
        # If OVA or other, keep it (user must import manually or script could be extended)
        return True
    except Exception as e:
        print("Extraction error:", e)
        return False


VAGRANTFILE_TEMPLATE = """# Generated Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.box = "{box}"
  config.vm.hostname = "{name}"
  config.vm.network "private_network", ip: "192.168.56.{ip_last}"
  config.vm.synced_folder ".", "/vagrant", type: "virtualbox"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 2048
    vb.cpus = 2
  end

  # Shell provisioner: try setup scripts or docker-compose
  config.vm.provision "shell", inline: <<-SHELL
    set -eux
    sudo apt-get update -y
    sudo apt-get install -y curl git build-essential
    # Install docker if docker-compose.yml exists
    if [ -f /vagrant/{lab_relative}/docker-compose.yml ]; then
      curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
      sudo usermod -aG docker vagrant || true
      # docker-compose plugin (modern)
      sudo apt-get install -y docker-compose-plugin || true
      cd /vagrant/{lab_relative}
      # best-effort: try docker compose up
      if command -v docker >/dev/null 2>&1; then
        sudo /usr/bin/docker compose up -d || sudo docker compose up -d || true
      fi
    fi

    # Run setup or install script if present
    if [ -x /vagrant/{lab_relative}/setup.sh ]; then
      cd /vagrant/{lab_relative} && sudo /vagrant/{lab_relative}/setup.sh || true
    elif [ -x /vagrant/{lab_relative}/install.sh ]; then
      cd /vagrant/{lab_relative} && sudo /vagrant/{lab_relative}/install.sh || true
    else
      echo "No setup/install script found in /vagrant/{lab_relative}. You may need to provision manually."
    fi
  SHELL
end
"""


def sanitize_name(s):
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in s)[:60]


def find_top_dir(path):
    # try to find most-likely project dir inside dest (avoid nested .git clones)
    entries = [p for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")]
    if len(entries) == 1:
        return entries[0].name
    return "."


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bootstrap_labs.py labs.txt")
        sys.exit(1)
    BASE_DIR.mkdir(exist_ok=True)
    with open(sys.argv[1], "r") as f:
        urls = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]
    ip_counter = 10
    for url in urls:
        try:
            name = sanitize_name(url.split("/")[-1] or "lab")
            lab_dir = BASE_DIR / name
            print("==> Processing:", url, "->", lab_dir)
            ok = clone_or_download(url, lab_dir)
            if not ok:
                print("Failed to fetch", url, " — skipping Vagrantfile creation")
                continue
            # try to detect top-level project dir
            lab_relative = find_top_dir(lab_dir)
            vagrantfile_content = VAGRANTFILE_TEMPLATE.format(
                box=BOX_NAME,
                name=name,
                ip_last=ip_counter % 250,
                lab_relative=lab_relative,
            )
            with open(lab_dir / "Vagrantfile", "w") as vf:
                vf.write(vagrantfile_content)
            print("Wrote Vagrantfile for", name)
            ip_counter += 1
        except Exception as e:
            print("Error handling", url, ":", e)
