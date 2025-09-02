from fastapi import APIRouter
from app.rag.vector_embedding import VectorEmbedding
from app.config import RAGConfig
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create-vectors")
async def rag_endpoint(payload: dict):
    
    logger.info(f"Received RAG request with payload: {payload}")
    VectorEmbed = VectorEmbedding()
    asyncio.create_task(VectorEmbed.create_vector_store())
    return "vector creation triggered successfully"

@router.post("/search-vectors")
async def search_vectors_endpoint(payload: dict):
    logger.info(f"Received search request with payload: {payload}")
    query = payload.get("query", "")
    VectorEmbed = VectorEmbedding()
    results = []
    op = await VectorEmbed.search(query)
    if op:
        for item in op:
            if isinstance(item, tuple) and len(item) == 2:
                chunk, distance = item
                results.append({
                    "chunk_info": chunk,
                    "distance": distance
                })
            else:
                logger.warning(f"Unexpected search result format: {item}")
    else:
        logger.info("No results found for the query.")
    return {"results": results}

@router.delete("/delete-all-vectors")
async def delete_all_vectors():
    """
    Deletes all vectors from the FAISS index.
    """
    VectorEmbed = VectorEmbedding()
    asyncio.create_task(VectorEmbed.clear_faiss_index())
    return "All vectors deleted successfully"