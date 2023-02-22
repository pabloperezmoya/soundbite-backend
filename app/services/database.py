import os
from bson import ObjectId
import pymongo
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

client = pymongo.MongoClient(DATABASE_URL)

class DatabaseService:
    def __init__(self):
        self.client = client
        

    # Audios
    def get_all_audios_from_user(self, user_id):
        collection = self.client["audio_app"]["audios"]
        return collection.find({"user_id": user_id})
    
    def append_audio_document(self, document):
        collection = self.client["audio_app"]["audios"]
        return collection.insert_one(document)

    def get_audio_document(self, _id):
        collection = self.client["audio_app"]["audios"]
        return collection.find_one({"_id": _id})

    def get_audio_from_user_id_and_stream_url(self, stream_url, user_id):
        collection = self.client["audio_app"]["audios"]
        return collection.find_one({"stream_url": stream_url, "user_id": user_id})

    def delete_audio_document(self, _id):
        collection = self.client["audio_app"]["audios"]
        return collection.delete_one({"_id": _id})

    def update_audio_document(self, audio_id, new_element):
        collection = self.client["audio_app"]["audios"]
        return collection.update_one({"_id": audio_id}, {"$set": new_element})

    # Users
    def get_all_users(self):
        collection = self.client["audio_app"]["users"]
        return collection.find()
    
    def get_user_by_email(self, email):
        collection = self.client["audio_app"]["users"]
        return collection.find({"email": email})

    def get_user_by_id(self, _id):
        collection = self.client["audio_app"]["users"]
        return collection.find({"_id": _id})

    def append_user_document(self, document):
        collection = self.client["audio_app"]["users"]
        return collection.insert_one(document)

    def upsert_token(self, user_id, token):
        collection = self.client["audio_app"]["users"]
        return collection.update_one({"_id": user_id}, {"$set": {"token": token}}, upsert=True)
        
    
    # Shares
    def create_share_document(self, document):
        collection = self.client["audio_app"]["shares"]
        return collection.insert_one(document)
    
    def get_share_document(self, document_id):
        collection = self.client["audio_app"]["shares"]
        return collection.find_one({"_id": ObjectId(document_id)})

