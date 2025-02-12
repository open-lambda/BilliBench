#!/usr/bin/env python3
"""
Script to generate payload for Func18_kmeans: generate dataset for KMeans and upload to GCP bucket.
"""

import os
import shutil
from google.cloud import storage
from sklearn.datasets import make_blobs
import numpy as np

# Function Configuration
APP_NAME = "App5_MlTraining"
FUNC_NAME = "Func18_kmeans"

# raise error if Environment variables are not set
if os.getenv("GCP_PROJECT") is None or os.getenv("GCP_BUCKET") is None:
    raise ValueError("GCP_PROJECT and GCP_BUCKET must be set")  

# GCP configuration
storage_client = storage.Client(project=os.getenv("GCP_PROJECT"))
bucket = storage_client.get_bucket(os.getenv("GCP_BUCKET"))

DATASET_DIR = os.path.join(os.getenv("BENCH_HOME"), "Dataset", APP_NAME, FUNC_NAME)

n_samples_dict = {
    "small": 2000,
    "medium": 50000,
    "large": 500000,
}

n_features_dict = {
    "small": 5,
    "medium": 40,
    "large": 40,
}

n_centers_dict = {
    "small": 10,
    "medium": 60,
    "large": 100,
}

def generate_dataset(size):
    """
    Generate dataset for KMeans.
    """
    n_samples = n_samples_dict[size]
    n_features = n_features_dict[size]
    n_centers = n_centers_dict[size]

    X, _ = make_blobs(n_samples=n_samples,
                      n_features=n_features,
                      centers=n_centers,
                      center_box=(-32, 32),
                      shuffle=True)

    np.save(os.path.join(DATASET_DIR, f"{size}_x.npy"), X)
    blob = bucket.blob(f"{FUNC_NAME}/{size}_x.npy")
    blob.chunk_size = 1<<30
    blob.upload_from_filename(os.path.join(DATASET_DIR, f"{size}_x.npy"))


def main():
    """
    Main function to generate dataset and upload to GCP bucket.
    """
    # clean up DATASET_DIR
    if os.path.exists(DATASET_DIR):
        shutil.rmtree(DATASET_DIR)
    os.makedirs(DATASET_DIR, exist_ok=True)

    for size in ["small", "medium", "large"]:
        generate_dataset(size)

if __name__ == "__main__":
    main()
