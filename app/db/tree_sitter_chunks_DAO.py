from app.db.mongodb import MongoDBAsync
from app.beans.chunks import Chunks
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TreeSitterChunksDAO(MongoDBAsync):
    def __init__(self):
        self.collection_name = "tree_sitter_chunks"
        super().__init__(collection_name=self.collection_name)
        
    async def insert_chunk(self, chunk: Chunks) -> None:
        """
        Insert a chunk into the MongoDB collection.
        """
        chunk_dict = chunk.get_chunk_info()
        metadata = chunk.get_chunk_metadata()
        async with self.gridfs.open_upload_stream(chunk.file_path, chunk_size_bytes=1024 * 1024 * 12, metadata=metadata) as stream:
            await stream.write(chunk.content.encode('utf-8'))
            
        await self.collection.insert_one(chunk_dict)
        
    async def get_chunks_by_file(self, file_path: str) -> list:
        """
        Get all chunks for a specific file and return as Chunks objects.
        """
        chunks = []
        async for file_doc in self.gridfs.find({"filename": file_path}):
            content = await file_doc.read()
            content_str = content.decode('utf-8')
            metadata = file_doc.metadata or {}
            chunk = Chunks(
                type=metadata.get('type'),
                content=content_str,
                file_path=metadata.get('file_path'),
                start_point=metadata.get('start_point'),
                end_point=metadata.get('end_point'),
                name=metadata.get('name'),
                hash=metadata.get('hash'),
                vector_id=metadata.get('vector_id')
            )
            chunks.append(chunk)
        return chunks
    async def delete_chunk(self, chunk_id: str) -> None:
        """
        Delete a chunk from the MongoDB collection.
        """
        await self.gridfs.delete(chunk_id)
        
        # await self.collection.delete_one({"_id": chunk_id})
    async def delete_chunks_by_file(self, file_path: str) -> None:
        """
        Delete all chunks for a specific file.
        """
        async for file_doc in self.gridfs.find({"filename": file_path}):
            await self.gridfs.delete(file_doc._id)

        # await self.collection.delete_many({"file_path": file_path})
        
    async def get_chunks_by_batch(self, batch_size: int):
        """
        Get chunks from GridFS in batches, including vector_id from metadata.
        """
        cursor = self.gridfs.find({})
        batch = []
        async for file_doc in cursor:
            content = await file_doc.read()
            content_str = content.decode('utf-8')
            metadata = file_doc.metadata or {}
            chunk = Chunks(
                type=metadata.get('type'),
                content=content_str,
                file_path=metadata.get('file_path'),
                start_point=metadata.get('start_point'),
                end_point=metadata.get('end_point'),
                name=metadata.get('name'),
                hash=metadata.get('hash'),
                vector_id=metadata.get('vector_id')
            )
            batch.append(chunk)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
            
                
    async def get_all_chunks(self) -> list:
        """
        Get all chunks from the MongoDB collection.
        """
        chunks = []
        async for file_doc in self.gridfs.find({}):
            content = await file_doc.read()
            content_str = content.decode('utf-8')
            metadata = file_doc.metadata or {}
            chunk = Chunks(
                type=metadata.get('type'),
                content=content_str,
                file_path=metadata.get('file_path'),
                start_point=metadata.get('start_point'),
                end_point=metadata.get('end_point'),
                name=metadata.get('name'),
                hash=metadata.get('hash'),
                vector_id=metadata.get('vector_id')
            )
            chunks.append(chunk)
        return chunks
    
    async def delete_all_chunks(self) -> None:
        """
        Delete all chunks from the MongoDB collection.
        """
        async for file_doc in self.gridfs.find({}):
            await self.gridfs.delete(file_doc._id)
    
    async def get_chunk_by_vector_id(self, vector_id: int) -> Chunks | None:
        """
        Get a chunk by its vector ID.
        """
        async for file_doc in self.gridfs.find({"metadata.vector_id": vector_id}):
            content = await file_doc.read()
            content_str = content.decode('utf-8')
            metadata = file_doc.metadata or {}
            return Chunks(
                type=metadata.get('type'),
                content=content_str,
                file_path=metadata.get('file_path'),
                start_point=metadata.get('start_point'),
                end_point=metadata.get('end_point'),
                name=metadata.get('name'),
                hash=metadata.get('hash'),
                vector_id=metadata.get('vector_id')
            )
        return None

    async def get_last_vector_id(self) -> int | None:
        """
        Get the last vector ID from the MongoDB collection.
        """
        cursor = self.gridfs.find({}, sort=[("metadata.vector_id", -1)])
        async for file_doc in cursor:
            metadata = file_doc.metadata or {}
            vector_id = metadata.get("vector_id")
            if isinstance(vector_id, int):
                return vector_id
            try:
                return int(vector_id)
            except (TypeError, ValueError):
                return -1
        return -1