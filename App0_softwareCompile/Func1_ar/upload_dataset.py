#!/usr/bin/env python3
"""
Script to generate payload for Func1_ar: clone Linux kernel, make Linux kernel, select a subset of .o files.
"""

import os
import shutil
import random
from git import Repo
from google.cloud import storage

# Function Configuration
APP_NAME = "App0_softwareCompile"
FUNC_NAME = "Func1_ar"
REPO_URL = "https://github.com/torvalds/linux.git"
TAG_NAME = "v6.13"

# raise error if Environment variables are not set
if os.getenv("GCP_PROJECT") is None or os.getenv("GCP_BUCKET") is None:
    raise ValueError("GCP_PROJECT and GCP_BUCKET must be set")

# GCP configuration
storage_client = storage.Client(project=os.getenv("GCP_PROJECT"))
bucket = storage_client.get_bucket(os.getenv("GCP_BUCKET"))

# Directory paths
CLONE_PARENT_DIR = os.path.join(os.getenv("BENCH_HOME"), "Dataset", APP_NAME, FUNC_NAME)
CLONE_DIR = os.path.join(CLONE_PARENT_DIR, "linux")

PAYLOAD_dirs = {
    "small": os.path.join(CLONE_PARENT_DIR, "payload_small"),
    "medium": os.path.join(CLONE_PARENT_DIR, "payload_medium"),
    "large": os.path.join(CLONE_PARENT_DIR, "payload_large"),
}

size_dict = {
    "small": 30,
    "medium": 300,
    "large": 3000,
}

def clone_linux_repo():
    """Clone Linux repository if it doesn't exist."""
    Repo.clone_from(REPO_URL, CLONE_DIR, depth=1, branch=TAG_NAME)
    print(f"Linux Repository (tag {TAG_NAME}) cloned into {CLONE_DIR}")
    
    """Run necessary kernel build preparation commands."""
    os.chdir(CLONE_DIR)
    os.system("make defconfig > /dev/null 2>&1 && make prepare > /dev/null 2>&1")
    os.system("make -j$(nproc) > /dev/null 2>&1")
    print(f"Linux Repository (tag {TAG_NAME}) built into {CLONE_DIR}")
    

def collect_object_files():
    """Collect all necessary .o files."""
    o_files = []
    for root, _, files in os.walk(CLONE_DIR):
        rel_root = os.path.relpath(root, CLONE_DIR)
        o_files.extend(
            os.path.join(root, f) for f in files if f.endswith(".o")
        )
    return o_files

def setup_payload_directory():
    o_files = collect_object_files()

    """Setup payload directory with a subset of .o files."""
    for size, payload_dir in PAYLOAD_dirs.items():
        os.makedirs(payload_dir, exist_ok=True)

        # Randomly select a subset of .o files
        subset_o_files = random.sample(o_files, size_dict[size])
        # Copy .o files
        for o_file in subset_o_files:
            rel_path = os.path.relpath(o_file, CLONE_DIR)
            dest_path = os.path.join(payload_dir, os.path.basename(o_file))
            shutil.copy(o_file, dest_path)

def upload_to_gcp(zip_file):
    """Upload zip file to gcp."""
    blob = bucket.blob(os.path.join(FUNC_NAME, os.path.basename(zip_file)))
    blob.upload_from_filename(zip_file)

def main():
    """Main execution function."""
    try:
        # clean up clone_parent_dir
        if os.path.exists(CLONE_PARENT_DIR):
            shutil.rmtree(CLONE_PARENT_DIR)
        os.makedirs(CLONE_PARENT_DIR, exist_ok=True)

        clone_linux_repo()
        setup_payload_directory()

        # zip each payload directory
        for size, payload_dir in PAYLOAD_dirs.items():
            shutil.make_archive(payload_dir, "zip", payload_dir)

            zip_file = os.path.join(CLONE_PARENT_DIR, f"payload_{size}.zip")
            upload_to_gcp(zip_file)

    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0
        
if __name__ == "__main__":
    main()