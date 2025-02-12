#! /usr/bin/env python3
"""
Script to generate payload for Func12_labelImage: download image and label from github.
"""

import os
import shutil
import random
from git import Repo
from google.cloud import storage
import urllib.request
# Function Configuration
APP_NAME = "App4_MLInference"
FUNC_NAME = "Func12_labelImage"

# raise error if Environment variables are not set
if os.getenv("GCP_PROJECT") is None or os.getenv("GCP_BUCKET") is None:
    raise ValueError("GCP_PROJECT and GCP_BUCKET must be set")

# GCP configuration
storage_client = storage.Client(project=os.getenv("GCP_PROJECT"))
bucket = storage_client.get_bucket(os.getenv("GCP_BUCKET"))

# Directory paths
DATASET_DIR = os.path.join(os.getenv("BENCH_HOME"), "Dataset", APP_NAME, FUNC_NAME)

def upload_image_to_gcp(image_url, image_name):
    """
    Upload image to GCP bucket.
    """
    # download image from url   
    image_path = os.path.join(DATASET_DIR, image_name)
    urllib.request.urlretrieve(image_url, image_path)

    # upload image to GCP bucket
    blob = bucket.blob(f"{FUNC_NAME}/{image_name}")
    blob.upload_from_filename(image_path)

def upload_label_to_gcp(label_url, label_name):
    """
    Upload label to GCP bucket.
    """
    # download label from url
    label_path = os.path.join(DATASET_DIR, label_name)
    urllib.request.urlretrieve(label_url, label_path)

    # upload label to GCP bucket
    blob = bucket.blob(f"{FUNC_NAME}/{label_name}")
    blob.upload_from_filename(label_path)

def main():
    """
    Main function to upload dataset to GCP bucket.
    """
    image_url = "https://raw.githubusercontent.com/spcl/serverless-benchmarks-data/refs/heads/master/400.inference/411.image-recognition/fake-resnet/512px-Cacatua_moluccensis_-Cincinnati_Zoo-8a.jpg"
    label_url = "https://raw.githubusercontent.com/raghakot/keras-vis/master/resources/imagenet_class_index.json"

    try:
        # clean up DATASET_DIR
        if os.path.exists(DATASET_DIR):
            shutil.rmtree(DATASET_DIR)
        os.makedirs(DATASET_DIR, exist_ok=True)

        # upload image and label to GCP bucket
        upload_image_to_gcp(image_url, "512px-Cacatua_moluccensis_-Cincinnati_Zoo-8a.jpg")
        upload_label_to_gcp(label_url, "imagenet_class_index.json")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    main()