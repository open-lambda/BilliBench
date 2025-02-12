#!/usr/bin/env python3
"""
Script to generate payload for Func14_knn: generate dataset for KNN and upload to GCP bucket.
"""

import os
import shutil
from google.cloud import storage
from sklearn.datasets import make_classification
import numpy as np

# Function Configuration
APP_NAME = "App5_MlTraining"
FUNC_NAME = "Func14_knn"

# raise error if Environment variables are not set
if os.getenv("GCP_PROJECT") is None or os.getenv("GCP_BUCKET") is None:
    raise ValueError("GCP_PROJECT and GCP_BUCKET must be set")

# GCP configuration
storage_client = storage.Client(project=os.getenv("GCP_PROJECT"))
bucket = storage_client.get_bucket(os.getenv("GCP_BUCKET"))

DATASET_DIR = os.path.join(os.getenv("BENCH_HOME"), "Dataset", APP_NAME, FUNC_NAME)

n_samples_dict = {
    "small": 2000,
    "medium": 500000,
    "large": 3125000,
}

n_features_dict = {
    "small": 5,
    "medium": 40,
    "large": 400,
}

n_informative_dict = {
    "small": 5,
    "medium": 40,
    "large": 400,
}

n_classes_dict = {
    "small": 2,
    "medium": 15,
    "large": 150,
}

def generate_dataset(size):
    """
    Generate dataset for KNN.
    """
    n_samples = n_samples_dict[size]
    n_features = n_features_dict[size]
    n_informative = n_informative_dict[size]
    n_classes = n_classes_dict[size]

    X, y = make_classification(n_samples=n_samples,
                               n_features=n_features,
                               n_informative=n_informative,
                               n_repeated=0,
                               n_redundant=0,
                               n_classes=n_classes,
                               random_state=777)

    np.save(os.path.join(DATASET_DIR, f"{size}_x.npy"), X)
    np.save(os.path.join(DATASET_DIR, f"{size}_y.npy"), y)

    blob = bucket.blob(f"{FUNC_NAME}/{size}_x.npy")
    blob.chunk_size = 1<<30
    blob.upload_from_filename(os.path.join(DATASET_DIR, f"{size}_x.npy"))

    blob = bucket.blob(f"{FUNC_NAME}/{size}_y.npy")
    blob.chunk_size = 1<<30
    blob.upload_from_filename(os.path.join(DATASET_DIR, f"{size}_y.npy"))

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
