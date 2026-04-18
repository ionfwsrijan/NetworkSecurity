import subprocess

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import sys

class S3Sync:
    def sync_folder_to_s3(self,folder,aws_bucket_url):
        try:
            command = ["aws", "s3", "sync", folder, aws_bucket_url]
            logging.info("Syncing local folder %s to %s", folder, aws_bucket_url)
            subprocess.run(command, check=True, capture_output=True, text=True)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def sync_folder_from_s3(self,folder,aws_bucket_url):
        try:
            command = ["aws", "s3", "sync", aws_bucket_url, folder]
            logging.info("Syncing S3 folder %s to %s", aws_bucket_url, folder)
            subprocess.run(command, check=True, capture_output=True, text=True)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
