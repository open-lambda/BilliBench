import os
import shutil
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

        # Temporary directory for processing
        with tempfile.TemporaryDirectory(dir=BENCH_HOME) as tmp_dir:
            payload_path = os.path.join(tmp_dir, f"payload_{events['size']}.zip")
            result_path = os.path.join(tmp_dir, "output.a")

            # Download payload from GCP bucket
            blob = bucket.blob(f"Func1_ar/payload_{events['size']}.zip")
            blob.chunk_size = 1 << 30  # 1GB chunks
            blob.download_to_filename(payload_path)

            # Unzip payload
            shutil.unpack_archive(payload_path, tmp_dir, "zip")

            # Run ar command
            args = f"find {tmp_dir} -name \"*.o\" | xargs ar rcs {result_path}"
            os.system(args)

            # Upload the compiled output to the bucket
            result_blob = bucket.blob(f"Func1_ar/output.a")
            result_blob.upload_from_filename(result_path)

        return 0

    except Exception as e:
        print(f"Error in handler: {e}")
        return 1

if __name__ == "__main__":
    try:
        # Run the function
        ret = handler({"size": "large"})
        print(f"Return value: {ret}")
    except Exception as e:
        print(f"Script failed: {e}")
