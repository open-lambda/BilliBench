import os, shutil, tempfile, json
import torch
from torchvision import transforms
from PIL import Image
from PIL import ImageFile
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
    models = {'small': 'mobilenet_v2', 'medium': 'resnet50', 'large': 'inception_v3'}
    resize_sizes = {'small': 256, 'medium': 256, 'large': 299}
    crop_sizes = {'small': 224, 'medium': 224, 'large': 299}
    try:
        # Initialize Google Cloud Storage
        bucket = initialize_storage(project_id, bucket_name)

        # Temporary directory for processing
        with tempfile.TemporaryDirectory(dir=BENCH_HOME) as tmp_dir:
            # download input image from GCP bucket
            blob = bucket.blob(f"Func12_labelImage/512px-Cacatua_moluccensis_-Cincinnati_Zoo-8a.jpg")
            blob.chunk_size = 1<<30
            blob.download_to_filename(os.path.join(tmp_dir, "input.jpg"))

            # download imagenet_class_index.json from GCP bucket
            blob = bucket.blob(f"Func12_labelImage/imagenet_class_index.json")
            blob.download_to_filename(os.path.join(tmp_dir, "imagenet_class_index.json"))

            # load the image and label
            input_image = Image.open(os.path.join(tmp_dir, "input.jpg"))
            label_index = json.load(open(os.path.join(tmp_dir, "imagenet_class_index.json"), 'r'))
            idx2label = [label_index[str(k)][1] for k in range(len(label_index))]

            preprocess = transforms.Compose([
                transforms.Resize(resize_sizes[events['size']]),
                transforms.CenterCrop(crop_sizes[events['size']]),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

            model = torch.hub.load('pytorch/vision:v0.10.0', models[events['size']], pretrained=True)
            model.eval()

            input_tensor = preprocess(input_image)
            input_batch = input_tensor.unsqueeze(0) 
            output = model(input_batch)


            _, index = torch.max(output, 1)
            ret = idx2label[index]

            return {'idx': index.item(), 'class': ret}
    except Exception as e:
        print(f"Error: {e}")
        return {'idx': -1, 'class': 'Error'}
            
if __name__ == "__main__":
    try:
        ret = handler({"size": "small"})
        print(f"Return value: {ret}")
    except Exception as e:
        print(f"Script failed: {e}")
