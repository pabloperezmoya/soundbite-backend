import requests
import os

from dotenv import load_dotenv

load_dotenv()

WRITE_URL = os.environ.get("WRITE_URL")
READ_URL = os.environ.get("READ_URL") # CDN
ACCESS_KEY = os.environ.get("ACCESS_KEY")

class StorageService:
    def get(self, filename) -> requests.Response:
        
        headers = {
            "AccessKey": ACCESS_KEY,
            "accept": "*/*"
        }
        s = requests.Session()
        response = s.get(READ_URL + filename, headers=headers, stream=True)
        return response

    def put(self, filename, data) -> requests.Response:
        headers = {
            "AccessKey": ACCESS_KEY,
            "content-type": "audio/mpeg"
        }
        response = requests.put(WRITE_URL + filename, data=data, headers=headers)
        return response

    def delete(self, filename) -> requests.Response:
        headers = {
            "AccessKey": ACCESS_KEY,
            "accept": "*/*"
        }
        response = requests.delete(WRITE_URL + filename, headers=headers)
        return response


