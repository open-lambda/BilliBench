#! /usr/bin/env python3
"""
Script to generate payload for Func8_mergesort: 
Generate matrix with different size, select a partition for them,and upload them to GCP bucket.
"""

import os
import shutil
import numpy as np
import numexpr as ne
from google.cloud import storage

# Function Configuration
APP_NAME = "App2_gensort"
FUNC_NAME = "Func8_mergesort"

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
    
    # select a partition for the matrix
    partition_path = os.path.join(PAYLOAD_DIRS[size], f"{size}.npy")
    pos = ne.evaluate("(matrix < " + str(50000) + ") & (matrix > " + str(0) + ")")
    partition = matrix[pos]
    np.save(partition_path, partition)

    # upload the result to GCP bucket
    bucket.blob(os.path.join("Func8_mergesort", size, f"{size}.npy")).upload_from_filename(partition_path)

def main():
    """Main function."""
    for size in matrix_sizes:
        generate_matrix(size)

if __name__ == "__main__":
    main()



