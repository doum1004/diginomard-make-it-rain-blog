import os
import requests
import base64
import html
from googleapiclient.discovery import build
from google_images_search import GoogleImagesSearch
from google.cloud import storage

try:
    from utils import SaveUtils
except ImportError:  # Python 3
    from .utils import SaveUtils
    
class GoogleCDN:
    api_key = os.getenv("GOOGLE_API_KEY")
    def __init__(self):
        pass

    def upload_to_bucket(blob_name, path_to_file, bucket_name):
        """ Upload data to a bucket"""
        
        # Explicitly use service account credentials by specifying the private key
        # file.
        storage_client = storage.Client.from_service_account_json(
            'creds.json')

        #print(buckets = list(storage_client.list_buckets())

        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(path_to_file)
        
        #returns a public url
        return blob.public_url