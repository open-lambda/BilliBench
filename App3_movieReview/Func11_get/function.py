import os
import tempfile
from google.cloud import storage

# Fetch required environment variables
BENCH_HOME = os.getenv("BENCH_HOME")
project_id = os.getenv("GCP_PROJECT")
bucket_name = os.getenv("GCP_BUCKET")

if not BENCH_HOME or not project_id or not bucket_name:
    raise EnvironmentError("Required environment variables (BENCH_HOME, GCP_PROJECT, GCP_BUCKET) are not set.")

def initialize_storage(project_id, bucket_name):
    """Initialize Google Cloud Storage client and bucket."""
    storage_client = storage.Client(project=project_id)
    return storage_client.get_bucket(bucket_name)

def handler(events):
    """
    Args: events (dict) including 'size' parameter.
    Returns: int 0 on success, raises exception on failure.
    """
    try:
        # Initialize Google Cloud Storage
        bucket = initialize_storage(project_id, bucket_name)  

        # download the string from the bucket Func11_get/{size}
        blob = bucket.blob(os.path.join('Func11_get', f"{events['size']}"))
        review = blob.download_as_string().decode('utf-8')
        print(len(review))
        
        # save to a tmp file
        with tempfile.TemporaryDirectory(dir=BENCH_HOME) as tmp_dir:   
            tmp_file_path = os.path.join(tmp_dir, f"output_{events['size']}.txt")
            with open(tmp_file_path, 'w') as f:
                f.write(review)

        return 0
    
    except Exception as e:
        print(f"Error in handler: {e}")
        return 1

if __name__ == "__main__":
    try:
        # Run the function
        ret = handler({"size": "small"})
        # ret = handler({"size": "medium"})
        # ret = handler({"size": "large"})
        print(f"Return value: {ret}")
    except Exception as e:
        print(f"Script failed: {e}")