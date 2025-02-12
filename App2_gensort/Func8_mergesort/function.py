import os
import tempfile
import numpy as np
from google.cloud import storage
import parallel_sort

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

        # Temporary directory for processing
        with tempfile.TemporaryDirectory(dir=BENCH_HOME) as tmp_dir:
            input_path = os.path.join(tmp_dir, f"{events['size']}.npy")
            output_path = os.path.join(tmp_dir, f"{events['size']}_sorted.npy")

            # Download payload from GCP bucket
            blob = bucket.blob(os.path.join("Func8_mergesort", events['size'], os.path.basename(input_path)))
            blob.chunk_size = 1<<30
            blob.download_to_filename(input_path)

            # Load the partition array
            partition_array = np.load(input_path)

            # Sort the partition array
            partition_array_sorted = parallel_sort.sort(partition_array)

            # save and upload the sorted partition array to GCP bucket
            np.save(output_path, partition_array_sorted)
            bucket.blob(os.path.join("Func8_mergesort", events['size'], os.path.basename(output_path))).upload_from_filename(output_path)

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
