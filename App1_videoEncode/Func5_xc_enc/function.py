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
            input_ivf_path = os.path.join(tmp_dir, f"{events['size']}.ivf")
            input_state_path = os.path.join(tmp_dir, f"{events['size']}.state")
            output_ivf_path = os.path.join(tmp_dir, f"output.ivf")
            xc_enc_path = os.path.join(tmp_dir, "xc-enc")
            
            # Download payload from GCP bucket
            bucket.blob(f"Func5_xc_enc/payload_{events['size']}.zip").download_to_filename(payload_path)
            
            # Unzip payload
            shutil.unpack_archive(payload_path, tmp_dir, "zip")
            os.system(f"chmod +x {xc_enc_path}")

            # Run xc-enc
            xc_enc_cmd = [xc_enc_path, "-o", output_ivf_path, "-I", input_state_path, input_ivf_path]
            os.system(" ".join(xc_enc_cmd))

            # Upload the result to GCP bucket
            bucket.blob(f"Func5_xc_enc/output.ivf").upload_from_filename(output_ivf_path)

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
