import os
from pathlib import Path
import shutil
from zipfile import ZipFile

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

Path('./tmp').mkdir(exist_ok=True)

blobs = list(storage_client.list_blobs(BUCKET_NAME))
latest_created_time = min([x.time_created for x in blobs])
latest_data_blob = [x for x in blobs if x.time_created == latest_created_time][0]
this_data_path = f'./tmp/{latest_data_blob.name}'
latest_data_blob.download_to_filename(this_data_path)

with ZipFile(this_data_path, 'r') as zipObj:
   zipObj.extractall()
