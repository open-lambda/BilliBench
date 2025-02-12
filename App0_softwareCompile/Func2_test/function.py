import os
import shutil
import tempfile
import subprocess
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
    Args: events (dict) including 'size' parameter; 'gtest_filter' parameter; 'workers_num' parameter.
    Returns: int 0 on success, raises exception on failure.
    """
    try:
        # Initialize Google Cloud Storage
        bucket = initialize_storage(project_id, bucket_name)

        # Temporary directory for processing
        with tempfile.TemporaryDirectory(dir=BENCH_HOME) as tmp_dir:
            # define the paths
            payload_path = os.path.join(tmp_dir, f"payload_{events['size']}.zip")
            gtest_parallel_py_path = os.path.join(tmp_dir, "gtest_parallel.py")
            gtest_parallel_path = os.path.join(tmp_dir, "gtest-parallel")
            test_binary_path = os.path.join(tmp_dir, f"{events['size']}_test_binary")
            result_path = os.path.join(tmp_dir, "output.txt")

            # Download payload from GCP bucket
            bucket.blob(f"Func2_test/payload_{events['size']}.zip").download_to_filename(payload_path)
            bucket.blob(f"Func2_test/gtest_parallel.py").download_to_filename(gtest_parallel_py_path)
            bucket.blob(f"Func2_test/gtest-parallel").download_to_filename(gtest_parallel_path)

            # unzip the payload and prepare the test binary
            shutil.unpack_archive(payload_path, tmp_dir, "zip")
            os.system(f"chmod +x {test_binary_path}")
            os.system(f"chmod +x {gtest_parallel_path}")

            # Run the test binary
            os.chdir(tmp_dir)
            test_cmds = ["./gtest-parallel", 
                         test_binary_path, 
                         "--gtest_filter=" + events['gtest_filter'], 
                         "--workers=" + str(events['workers_num']),
                         "> " + result_path]

            os.system(" ".join(test_cmds))

            # Upload the result to GCP bucket
            result_blob = bucket.blob(f"Func2_test/output_{events['size']}.txt")
            result_blob.upload_from_filename(result_path)

        return 0

    except Exception as e:
        print(f"Error in handler: {e}")
        return 1
            

if __name__ == "__main__":
    try:
        ret = handler({"size": "small", "gtest_filter": "", "workers_num": 1})
        # ret = handler({"size": "medium", "gtest_filter": "*VP9DecodeMultiThreadedTest*", "workers_num": 16})
        # ret = handler({"size": "large", "gtest_filter": "*VP9*", "workers_num": 24})
        print(f"Return value: {ret}")
    except Exception as e:
        print(f"Error in handler: {e}")
