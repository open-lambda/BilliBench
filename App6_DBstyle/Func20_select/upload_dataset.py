#!/usr/bin/env python3
"""
Script to generate payload for Func20_select: generate dataset for Select and upload to GCP bucket.
"""

import os
import shutil
from google.cloud import storage
import numpy as np
import pandas as pd

# Function Configuration
APP_NAME = "App6_DBstyle"
FUNC_NAME = "Func20_select"

# raise error if Environment variables are not set
if os.getenv("GCP_PROJECT") is None or os.getenv("GCP_BUCKET") is None:
    raise ValueError("GCP_PROJECT and GCP_BUCKET must be set")

# GCP configuration
storage_client = storage.Client(project=os.getenv("GCP_PROJECT"))
bucket = storage_client.get_bucket(os.getenv("GCP_BUCKET"))

DATASET_DIR = os.path.join(os.getenv("BENCH_HOME"), "Dataset", APP_NAME, FUNC_NAME)

N_dict = {
    "small": 2000000,
    "medium": 50000000,
    "large": 100000000,
}

K_dict = {
    "small": 2000,
    "medium": 20000,
    "large": 40000,
}

def generate_dataset(size):
    N = N_dict[size]
    K = K_dict[size]

    # generate the dataset
    DT = {}
    DT["id0"] = np.random.randint(K, size=N)  
    DT["id1"] = np.random.randint(N/K, size=N)  
    DT["id2"] = np.random.randint(K, size=N)
    DT["id3"] = np.random.randint(N/K, size=N)                 
    DT["id4"] = np.random.randint(K, size=N)  
    DT["id5"] = np.random.randint(K, size=N)
    DT["id6"] = np.random.randint(N/K, size=N)   
    DT["id7"] = np.random.randint(K, size=N)  
    DT["id8"] = np.random.randint(K, size=N)
    DT["id9"] = np.random.randint(N/K, size=N) 
    DT["id10"] = np.random.randint(K, size=N)  
    DT["id11"] = np.random.randint(N/K, size=N)  
    DT["id12"] = np.random.randint(K, size=N)
    DT["id13"] = np.random.randint(N/K, size=N)                 
    DT["id14"] = np.random.randint(K, size=N)  
    DT["id15"] = np.random.randint(K, size=N)
    DT["id16"] = np.random.randint(N/K, size=N)   
    DT["id17"] = np.random.randint(K, size=N)  
    DT["id18"] = np.random.randint(K, size=N)
    DT["id19"] = np.random.randint(N/K, size=N)   

    DT["v1"] =  np.random.randint(N, size=N)   
    DT["v2"] =  np.random.randint(N, size=N)   
    DT["v3"] =  np.random.randint(100, size=N)   
    DT["v4"] =  np.random.randint(N, size=N)   
    DT["v5"] =  np.random.randint(N, size=N)

    df = pd.DataFrame(data = DT)
    df.to_csv(os.path.join(DATASET_DIR, f"{size}.csv"), index=False)

    blob = bucket.blob(f"{FUNC_NAME}/{size}.csv")
    blob.chunk_size = 1<<30
    blob.upload_from_filename(os.path.join(DATASET_DIR, f"{size}.csv"))

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
