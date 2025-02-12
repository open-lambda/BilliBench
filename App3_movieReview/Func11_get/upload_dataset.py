#! /usr/bin/env python3
"""
Script to generate payload for Func10_dynamicHtml: generate a dynamic html page.
"""

import os
import shutil
import random
from git import Repo
from google.cloud import storage

# Function Configuration
APP_NAME = "App3_movieReview"
FUNC_NAME = "Func11_get"

# raise error if Environment variables are not set
if os.getenv("GCP_PROJECT") is None or os.getenv("GCP_BUCKET") is None:
    raise ValueError("GCP_PROJECT and GCP_BUCKET must be set")

# GCP configuration
storage_client = storage.Client(project=os.getenv("GCP_PROJECT"))
bucket = storage_client.get_bucket(os.getenv("GCP_BUCKET"))

# Directory paths
PARENT_DIR = os.path.join(os.getenv("BENCH_HOME"), "Dataset", APP_NAME, FUNC_NAME)


size_dict = {
    "small": 10000,
    "medium": 5000000,
    "large": 512000000,
}

def upload_contents():
    """Upload the contents to the bucket."""
    for size, content_length in size_dict.items():
        content = "0" * content_length
        blob = bucket.blob(os.path.join(FUNC_NAME, f"{size}"))
        blob.upload_from_string(content)


if __name__ == "__main__":
    """Main execution function."""
    try:
        upload_contents()
    except Exception as e:
        print(f"Error: {e}")
