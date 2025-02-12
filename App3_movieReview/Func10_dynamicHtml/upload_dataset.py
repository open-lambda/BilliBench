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
FUNC_NAME = "Func10_dynamicHtml"

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

def upload_html_template():
    """Upload the html template to the bucket."""
    template_html = """<!DOCTYPE html>
<html>
  <head>
    <title>Randomly generated data.</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="http://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <style type="text/css">
      .container {
        max-width: 500px;
        padding-top: 100px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <p>Welcome {{username}}!</p>
      <p>Data generated at: {{cur_time}}!</p>
      <p>Requested random numbers: {{random_numbers}}</p>
    </div>
  </body>
</html>"""
    bucket.blob(os.path.join(FUNC_NAME, f"html_template")).upload_from_string(template_html)

def upload_contents():
    """Upload the contents to the bucket."""
    for size, content_length in size_dict.items():
        content = "0" * content_length
        blob = bucket.blob(os.path.join(FUNC_NAME, f"{size}"))
        blob.upload_from_string(content)


if __name__ == "__main__":
    """Main execution function."""
    try:
        upload_html_template()
        upload_contents()
    except Exception as e:
        print(f"Error: {e}")
