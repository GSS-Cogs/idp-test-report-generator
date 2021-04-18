
from datetime import datetime
import os
import zipfile

from google.cloud import storage

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

all_the_files = []
for root, dirs, files in os.walk("./out/allure-results"):
    root = root[6:]
    assert root.startswith("allure-results"), f'expectied to start with "allure-results/" but got {root}'
    for file in files:
        all_the_files.append(f'./out/{root}/{file}')

for root, dirs, files in os.walk("./out/allure-report"):
    root = root[6:]
    assert root.startswith("allure-report"), f'expectied to start with "allure-report/" but got {root}'
    for file in files:
        all_the_files.append(f'./out/{root}/{file}')

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        if root == "./out/seeds":
            continue
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

output_name = datetime.now().isoformat()
zipf = zipfile.ZipFile(f'{output_name}.zip', 'w', zipfile.ZIP_DEFLATED)
zipdir('./out', zipf)
zipf.close()   

storage_client = get_client()
bucket = storage_client.get_bucket(BUCKET_NAME)

blob = bucket.blob(f'{output_name}.zip')
blob.upload_from_filename(f'{output_name}.zip')
