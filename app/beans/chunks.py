class Chunks:
    
    def __init__(self, chunk=None, **kwargs):
        if chunk and isinstance(chunk, dict):
            # Initialize from dictionary
            self.type = chunk.get('type', None)
            self.content = chunk.get('content', None)
            self.file_path = chunk.get('file_path', None)
            self.start_point = chunk.get('start_point', None)
            self.end_point = chunk.get('end_point', None)
            self.name = chunk.get('name', None)
            self.hash = chunk.get('hash', None)
            self.vector_id = chunk.get('vector_id', None)
        else:
            # Initialize from keyword arguments
            self.type = kwargs.get('type', None)
            self.content = kwargs.get('content', None)
            self.file_path = kwargs.get('file_path', None)
            self.start_point = kwargs.get('start_point', None)
            self.end_point = kwargs.get('end_point', None)
            self.name = kwargs.get('name', None)
            self.hash = kwargs.get('hash', None)
            self.vector_id = kwargs.get('vector_id', None)

    def get_chunk_info(self):
        """
        Returns a dictionary representation of the chunk.
        """
        return {
            "type": self.type,
            "content": self.content,
            "file_path": self.file_path,
            "start_point": self.start_point,
            "end_point": self.end_point,
            "name": self.name,
            "hash": self.hash
        }
    def get_chunk_metadata(self):
        """
        Returns the metadata of the chunk.
        """
        return {
            "type": self.type,
            "file_path": self.file_path,
            "start_point": self.start_point,
            "end_point": self.end_point,
            "name": self.name,
            "hash": self.hash,
            "vector_id": self.vector_id
        }

    def get_chunk_content(self):
        """
        Returns the content of the chunk.
        """
        return self.content