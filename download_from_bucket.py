import os 
import shutil

from pathlib import Path
from google.cloud import storage

# Rmove left overs from last run
if os.path.isdir("out"):
    shutil.rmtree("out")

BUCKET_NAME = os.environ["REPORT_BUCKET_NAME"]

def get_client():
    """
    Get a storage client
    """
    try:
        storage_client = storage.Client()
    except Exception as err:
        raise Exception("Unable to get storage client. Aborting operation:") from err
        
    return storage_client

storage_client = get_client()
blobs = storage_client.list_blobs(BUCKET_NAME)

result_path = Path("out/allure-results")
result_path.mkdir(exist_ok=True, parents=True)

result_path = Path("out/allure-report")
result_path.mkdir(exist_ok=True, parents=True)

os.chdir('./out')

for blob in storage_client.list_blobs(BUCKET_NAME):
    if not blob.name.endswith("/"): # don't download empty directories
        if "/" in blob.name:
            needs_path = "/".join(str(blob.name).split("/")[:-1])
            this_path = Path(needs_path)
            this_path.mkdir(exist_ok=True, parents=True)
        blob.download_to_filename(blob.name)

bucket = storage_client.bucket(BUCKET_NAME)
for blob in storage_client.list_blobs(BUCKET_NAME):
    blob_to_go = bucket.blob(blob.name)
    blob_to_go.delete()