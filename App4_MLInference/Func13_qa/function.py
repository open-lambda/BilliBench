from google.cloud import storage
from transformers import pipeline
import os

# Fetch required environment variables
BENCH_HOME = os.getenv("BENCH_HOME")
project_id = os.getenv("GCP_PROJECT")
bucket_name = os.getenv("GCP_BUCKET")

if not BENCH_HOME or not project_id or not bucket_name:
    raise EnvironmentError("Required environment variables (BENCH_HOME, GCP_PROJECT, GCP_BUCKET) are not set.")

models = {}

def load_models():
    models['small'] = pipeline("question-answering", model='distilbert-base-uncased-distilled-squad')
    models['medium'] = pipeline("question-answering", model='bert-large-uncased-whole-word-masking-finetuned-squad')
    models['large'] = pipeline("text-generation", model='gpt2-large')
    

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
        if events['task_type'] == 'qa':
            result = models[events['size']](events['question'], events['context'])['answer']

        elif events['task_type'] == 'text_gen':
            result = models[events['size']](events['prompt'], max_length=200)[0]

        else:
            raise ValueError(f"Invalid task type: {events['task_type']}")
            
        return result

    except Exception as e:
        print(f"Error in handler: {e}")
        return 1

if __name__ == "__main__":
    try:
        load_models()
        # result = handler({'size': 'small', 
        #          'task_type': 'qa', 
        #          'question': 'What is the capital of France?', 
        #          'context': 'France is a country in Western Europe. Its capital is Paris, a major European city known for its art, fashion, and culture.'})
        # result = handler({'size': 'medium', 
        #          'task_type': 'qa', 
        #          'question': 'What is the capital of France?', 
        #          'context': 'France is a country in Western Europe. Its capital is Paris, a major European city known for its art, fashion, and culture.'})
        result = handler({'size': 'large', 
                 'task_type': 'text_gen', 
                 'prompt': 'Once upon a time'})
        print(result)
    except Exception as e:
        print(f"Error in main: {e}")
