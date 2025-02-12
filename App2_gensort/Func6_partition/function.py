
import os
import tempfile
from google.cloud import storage
import numpy as np
import numexpr as ne
import concurrent.futures

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

def partition_array_segment(a, i, mapper_dir, gcp_bucket, size):
    min_limit = i * 50000
    max_limit = min(50000 * (i + 1), 5000000)
    pos = ne.evaluate("(a < " + str(max_limit) + ") & (a > " + str(min_limit) + ")")
    part = a[pos]

    np.save(os.path.join(mapper_dir, str(i) + ".npy"), part)

    # upload the result to GCP bucket
    gcp_bucket.blob(os.path.join("Func6_partition", size, str(i) + ".npy")).upload_from_filename(os.path.join(mapper_dir, str(i) + ".npy"))
    
def wrapper_function(args):
    partition_array_segment(*args)
    return 1

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
            mapper_dir = os.path.join(tmp_dir, "mapper")
            os.makedirs(mapper_dir, exist_ok=True)

            # Download payload from GCP bucket
            blob = bucket.blob(os.path.join("Func6_partition", os.path.basename(dat_path)))
            blob.chunk_size = 1<<30
            blob.download_to_filename(dat_path)

            # Load the matrix
            matrix = np.memmap(dat_path, dtype='uint32', mode='r', shape=(matrix_sizes[events['size']],))

            # Partition the matrix
            with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
                futures = []
                for i in range(100):
                    futures.append(executor.submit(wrapper_function, (matrix, i, mapper_dir, bucket, events['size'])))
                for future in concurrent.futures.as_completed(futures):
                    pass

        return 0

    except Exception as e:
        print(f"Error in handler: {e}")
        return 1

if __name__ == "__main__":
    try:
        # Run the function
        ret = handler({"size": "medium"})
        print(f"Return value: {ret}")
    except Exception as e:
        print(f"Script failed: {e}")
