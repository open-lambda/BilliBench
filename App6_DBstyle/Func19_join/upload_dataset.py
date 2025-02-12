#!/usr/bin/env python3
"""
Script to generate payload for Func19_join: generate dataset for Join and upload to GCP bucket.
"""

import os
import shutil
from google.cloud import storage
import numpy as np
import pandas as pd

# Function Configuration
APP_NAME = "App6_DBstyle"
FUNC_NAME = "Func19_join"

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

    # generate join1
    DT = {}
    DT["id0"] = np.arange(N)
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
    df.to_csv(os.path.join(DATASET_DIR, f"{size}_join1.csv"), index=False)

    blob = bucket.blob(f"{FUNC_NAME}/{size}_join1.csv")
    blob.chunk_size = 1<<30
    blob.upload_from_filename(os.path.join(DATASET_DIR, f"{size}_join1.csv"))

    # generate join2
    DT = {}
    DT["id0"] = np.arange(N)
    DT["v6"] =  np.random.randint(N, size=N)   
    df = pd.DataFrame(data = DT)
    df.to_csv(os.path.join(DATASET_DIR, f"{size}_join2.csv"), index=False)

    blob = bucket.blob(f"{FUNC_NAME}/{size}_join2.csv")
    blob.chunk_size = 1<<30
    blob.upload_from_filename(os.path.join(DATASET_DIR, f"{size}_join2.csv"))

def main():
    """
    Main function to generate dataset and upload to GCP bucket.
    """
    # clean up DATASET_DIR
    if os.path.exists(DATASET_DIR):
        shutil.rmtree(DATASET_DIR)
    os.makedirs(DATASET_DIR, exist_ok=True)

    for size in ["small"]:
        generate_dataset(size)

if __name__ == "__main__":
    main()


# # N = 20000000
# # K = 2000
# # DT = {}
# DT["id0"] = np.arange(N)
# DT["id1"] = np.random.randint(N/K, size=N)  
# DT["id2"] = np.random.randint(K, size=N)
# DT["id3"] = np.random.randint(N/K, size=N)                 
# DT["id4"] = np.random.randint(K, size=N)  
# DT["id5"] = np.random.randint(K, size=N)
# DT["id6"] = np.random.randint(N/K, size=N)   
# DT["id7"] = np.random.randint(K, size=N)  
# DT["id8"] = np.random.randint(K, size=N)
# DT["id9"] = np.random.randint(N/K, size=N) 
# DT["id10"] = np.random.randint(K, size=N)  
# DT["id11"] = np.random.randint(N/K, size=N)  
# DT["id12"] = np.random.randint(K, size=N)
# DT["id13"] = np.random.randint(N/K, size=N)                 
# DT["id14"] = np.random.randint(K, size=N)  
# DT["id15"] = np.random.randint(K, size=N)
# DT["id16"] = np.random.randint(N/K, size=N)   
# DT["id17"] = np.random.randint(K, size=N)  
# DT["id18"] = np.random.randint(K, size=N)
# DT["id19"] = np.random.randint(N/K, size=N)   
# # # 80 byte in total

# DT["v1"] =  np.random.randint(N, size=N)   
# DT["v2"] =  np.random.randint(N, size=N)   
# DT["v3"] =  np.random.randint(100, size=N)   
# DT["v4"] =  np.random.randint(N, size=N)   
# DT["v5"] =  np.random.randint(N, size=N)

# # # 20 byte in total

# # print("generate finishes")

# # df = pd.DataFrame(data = DT)
# # df.to_csv('small_join1.csv', index=False)


# # N = 20000000
# # K = 2000
# # DT = {}
# # DT["id0"] = np.arange(N)

# # # 80 byte in total

# # DT["v6"] =  np.random.randint(N, size=N)   

# # # 20 byte in total

# # print("generate finishes")

# # df = pd.DataFrame(data = DT)
# # df.to_csv('small_join1.csv', index=False)


# # # N = 50000000
# # # K = 20000

# # # N = 100000000
# # # K = 40000