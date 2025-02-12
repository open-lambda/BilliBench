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
    Args: events (dict) including 'size' parameter, 'quality' parameter, 'thread_number' parameter.
    Returns: int 0 on success, raises exception on failure.
    """
    try:
        # Initialize Google Cloud Storage
        bucket = initialize_storage(project_id, bucket_name)

        # Temporary directory for processing
        with tempfile.TemporaryDirectory(dir=BENCH_HOME) as tmp_dir:
            payload_path = os.path.join(tmp_dir, f"payload_{events['size']}.zip")
            output_state_path = os.path.join(tmp_dir, f"{events['size']}.state")
            output_ivf_path = os.path.join(tmp_dir, f"{events['size']}.ivf")
            input_y4m_path = os.path.join(tmp_dir, f"output.y4m")
            xc_dump_path = os.path.join(tmp_dir, "xc-dump")
            vpxenc_path = os.path.join(tmp_dir, "vpxenc")

            # Download payload from GCP bucket
            bucket.blob(f"Func4_xc_dump/payload_{events['size']}.zip").download_to_filename(payload_path)

            # Unzip payload
            shutil.unpack_archive(payload_path, tmp_dir, "zip")
            os.system(f"chmod +x {xc_dump_path}")
            os.system(f"chmod +x {vpxenc_path}")
            
            # Run vpxenc
            vpxenc_cmd = [vpxenc_path, "--ivf", "-q", "--codec=vp8", "--" + events['quality'], 
                          "--threads=" + str(events['thread_number']), "-o", output_ivf_path, input_y4m_path]
            os.system(" ".join(vpxenc_cmd))

            # Run xc-dump
            xc_dump_cmd = [xc_dump_path, output_ivf_path, output_state_path]    
            os.system(" ".join(xc_dump_cmd))

            # Upload the result to GCP bucket  
            bucket.blob(f"Func4_xc_dump/{events['size']}.state").upload_from_filename(output_state_path)
            bucket.blob(f"Func4_xc_dump/{events['size']}.ivf").upload_from_filename(output_ivf_path)

        return 0

    except Exception as e:
        print(f"Error in handler: {e}")
        return 1
    
if __name__ == "__main__":
    try:
        # Run the function
        # ret = handler({"size": "small", "quality": "rt", "thread_number": 1})
        ret = handler({"size": "medium", "quality": "good", "thread_number": 10})
        # ret = handler({"size": "large", "quality": "best", "thread_number": 10})
        print(f"Return value: {ret}")
    except Exception as e:
        print(f"Script failed: {e}")
