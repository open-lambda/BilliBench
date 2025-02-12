#! /usr/bin/env python3
"""
Script to generate payload for Func7_sample: 
Generate matrix with different size, and upload them to GCP bucket.
"""

import os
import shutil
import requests
import numpy as np
from google.cloud import storage

# Function Configuration
APP_NAME = "App2_gensort"
FUNC_NAME = "Func7_sample"

# GCP configuration
storage_client = storage.Client(project=os.getenv("GCP_PROJECT"))
bucket = storage_client.get_bucket(os.getenv("GCP_BUCKET"))

# Directory paths
PARENT_DIR = os.path.join(os.getenv("BENCH_HOME"), "Dataset", APP_NAME, FUNC_NAME)

PAYLOAD_DIRS = {
    "small": os.path.join(PARENT_DIR, "payload_small"),
    "medium": os.path.join(PARENT_DIR, "payload_medium"),
    "large": os.path.join(PARENT_DIR, "payload_large"),
}

matrix_sizes = {
    "small": 1024*1024*25,
    "medium": 1024*1024*256,
    "large": 1024*1024*256*10,
}

def generate_matrix(size):
    """Generate matrix with different size."""
    # generate payload directory
    os.makedirs(PAYLOAD_DIRS[size], exist_ok=True)

    # generate matrix
    dat_path = os.path.join(PAYLOAD_DIRS[size], f"{size}.dat")
    matrix = np.memmap(dat_path, dtype='uint32', mode='w+', shape=(matrix_sizes[size],))
    matrix[:] = np.random.randint(5000000, size=(matrix_sizes[size],), dtype=np.uint32)
    matrix.flush()
    
    # upload matrix to GCP bucket
    blob = bucket.blob(os.path.join(FUNC_NAME, os.path.basename(dat_path)))
    blob.upload_from_filename(dat_path)

def main():
    """Main function."""
    for size in matrix_sizes:
        generate_matrix(size)

if __name__ == "__main__":
    main()



