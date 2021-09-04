import firebase_admin
from firebase_admin import credentials, storage, firestore
# from google.cloud import storage
from . import config_file

cred = credentials.Certificate(config_file.FIREBASE_STORAGE_PATH)
firebase_admin.initialize_app(
    cred, {
        "storageBucket": config_file.FIREBASE_BUCKET,
    })

bucket = storage.bucket()
db = firestore.client()
timestamp = firestore.SERVER_TIMESTAMP
