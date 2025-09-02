import pymongo
import gridfs
from app.config import RAGConfig
class MongoDBAsync:
    def __init__(self, collection_name="test"):
        self.db_name = RAGConfig().db_name
        self.client = pymongo.AsyncMongoClient(RAGConfig().mongo_uri)
        self.db = self.client[self.db_name]
        self.collection = self.db[collection_name]
        self.gridfs = gridfs.AsyncGridFSBucket(self.db, bucket_name=collection_name+"_gridfs")
