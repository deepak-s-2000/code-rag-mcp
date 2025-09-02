import os
import asyncio
from app.helpers.file_parser import FileParser
from app.config import RAGConfig
from app.db.tree_sitter_chunks_DAO import TreeSitterChunksDAO
import logging
class CodeBaseParser:
    def __init__(self, RootPath):
        logging.basicConfig(level=logging.INFO)
        self.RootPath = RootPath
        self.accepted_file_types = tuple(RAGConfig().accepted_file_types)
        self.tree_sitter_chunks_dao = TreeSitterChunksDAO()
        self.codebase_path = RAGConfig().codebase_path

    async def parse_code(self):
        for (root, dirs, files) in os.walk(self.RootPath):
            for file in files:
                if file.endswith(self.accepted_file_types):
                    file_path = os.path.join(root, file)
                    logging.info(f"Parsing file: {file_path}")
                    file_parser = FileParser(file_path)
                    chunks = await file_parser.parse_file()
                    for chunk in chunks:
                        chunk.vector_id = await self.tree_sitter_chunks_dao.get_last_vector_id()+1
                        await self.tree_sitter_chunks_dao.insert_chunk(chunk)

async def code_base_parser():
    root_path = RAGConfig().codebase_path
    code_base_parser = CodeBaseParser(root_path)
    # await code_base_parser.parse_code()
    chunks = await code_base_parser.tree_sitter_chunks_dao.get_chunks_by_file("codebase\\python_codebase\\fastapi-with-mongodb\\app\\main.py")
    for chunk in chunks:
        print(f"Type: {chunk.type}, Content:\n{chunk.content}\n")
if __name__ == "__main__":
    asyncio.run(code_base_parser())