import os
import tempfile
from google.cloud import storage
import numpy as np
import random

# Fetch required environment variables
BENCH_HOME = os.getenv("BENCH_HOME")
project_id = os.getenv("GCP_PROJECT")
bucket_name = os.getenv("GCP_BUCKET")

if not BENCH_HOME or not project_id or not bucket_name: 
    raise EnvironmentError("Required environment variables (BENCH_HOME, GCP_PROJECT, GCP_BUCKET) are not set.") 

matrix_sizes = {
    "small": 1024*1024*25,
    "medium": 1024*1024*256,
    "large": 1024*1024*256*10,
}

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

        # Temporary directory for processing
        with tempfile.TemporaryDirectory(dir=BENCH_HOME) as tmp_dir:
            dat_path = os.path.join(tmp_dir, f"{events['size']}.dat")

            # Download payload from GCP bucket
            blob = bucket.blob(os.path.join("Func7_sample", os.path.basename(dat_path)))
            blob.chunk_size = 1<<30
            blob.download_to_filename(dat_path)

            matrix = np.memmap(dat_path, dtype='uint32', mode='r', shape=(matrix_sizes[events['size']],))
            results = []
            for _ in range(1024*128):
                results.append(str(matrix[random.randint(0, matrix_sizes[events['size']]-1)]))

            # upload the result to GCP bucket
            bucket.blob(os.path.join("Func7_sample", f"{events['size']}_result.txt")).upload_from_string("\n".join(results))

        return 0

    except Exception as e:
        print(f"Error in handler: {e}")
        return 1

if __name__ == "__main__":
    try:
        # Run the function
        ret = handler({"size": "small"})
        print(f"Return value: {ret}")
    except Exception as e:
        print(f"Script failed: {e}")
