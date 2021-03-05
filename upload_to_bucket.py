
import os
from os import listdir
from os.path import isfile, join

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

storage_client = get_client()
bucket = storage_client.get_bucket(BUCKET_NAME)


result_files = []
for root, dirs, files in os.walk("./out/allure-results"):
    root = root[6:]
    assert root.startswith("allure-results"), f'expectied to start with "allure-results/" but got {root}'
    for file in files:
        result_files.append(f'{root}/{file}')

report_files = []
for root, dirs, files in os.walk("./out/allure-report"):
    root = root[6:]
    assert root.startswith("allure-report"), f'expectied to start with "allure-report/" but got {root}'
    for file in files:
        report_files.append(f'{root}/{file}')

for result_file in result_files:
    blob = bucket.blob(result_file)
    blob.upload_from_filename(f'./out/{result_file}')

for report_file in report_files:
    blob = bucket.blob(report_file)
    blob.upload_from_filename(f'./out/{report_file}')
