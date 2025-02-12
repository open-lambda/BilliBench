from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import os
import tempfile
import pickle
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
            # define the paths
            X_path = os.path.join(tmp_dir, f"{events['size']}_x.npy")
            y_path = os.path.join(tmp_dir, f"{events['size']}_y.npy")

            # download the dataset from GCP bucket
            bucket.blob(f"Func14_knn/{events['size']}_x.npy").download_to_filename(X_path)
            bucket.blob(f"Func14_knn/{events['size']}_y.npy").download_to_filename(y_path)

            # load the dataset
            X = np.load(X_path)
            y = np.load(y_path)

            # train the KNN classifier
            knn_clsf = KNeighborsClassifier(n_neighbors=3,
                                          weights='uniform',
                                          algorithm='kd_tree',
                                          metric='euclidean')
            alg = knn_clsf.fit(X, y)

            # save the model
            model_path = os.path.join(tmp_dir, f"{events['size']}_knn_model.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(alg, f)

            # upload the model to GCP bucket
            bucket.blob(f"Func14_knn/{events['size']}_knn_model.pkl").upload_from_filename(model_path)

            return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1
    
if __name__ == "__main__":
    try:
        ret = handler({"size": "small"})
        print(f"Return value: {ret}")
    except Exception as e:
        print(f"Error: {e}")
