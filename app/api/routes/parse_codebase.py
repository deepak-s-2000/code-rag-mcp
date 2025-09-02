from fastapi import APIRouter
from app.core.CodeBaseParser import CodeBaseParser
from app.config import RAGConfig
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/parse")
async def parse_codebase():
    asyncio.create_task(CodeBaseParser(RAGConfig().codebase_path).parse_code())
    # Process the data
    logger.info("Codebase parsed successfully")
    return {"message": "Codebase parsed successfully"}

@router.get("/get-chunks-by-filename")
async def get_chunks_by_filename(file_path: str):
    """
    Get all chunks for a specific file.
    """
    code_base_parser = CodeBaseParser(RAGConfig().codebase_path)
    chunks = await code_base_parser.tree_sitter_chunks_dao.get_chunks_by_file(file_path)
    logger.info(f"Retrieved {len(chunks)} chunks for file: {file_path}")
    return {"chunks": [chunk.get_chunk_info() for chunk in chunks]}

@router.delete("/delete-chunks-by-filename")
async def delete_chunks_by_filename(file_path: str):
    """
    Delete all chunks for a specific file.
    """
    code_base_parser = CodeBaseParser(RAGConfig().codebase_path)
    await code_base_parser.tree_sitter_chunks_dao.delete_chunks_by_file(file_path)
    logger.info(f"Deleted chunks for file: {file_path}")
    return {"message": "Chunks deleted successfully"}

@router.delete("/delete-all-chunks")
async def delete_all_chunks():
    """
    Delete all chunks from the MongoDB collection.
    """
    code_base_parser = CodeBaseParser(RAGConfig().codebase_path)
    asyncio.create_task(code_base_parser.tree_sitter_chunks_dao.delete_all_chunks())
    logger.info("All chunks deleted successfully")
    return {"message": "All chunks deleted successfully"}