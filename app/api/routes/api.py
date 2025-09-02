
from app.api.routes.parse_codebase import router as parse_codebase_router
from app.api.routes.rag_api import router as rag_api_router
from fastapi import APIRouter
from app.config import RAGConfig 
import time
import requests
router = APIRouter()
router.include_router(parse_codebase_router)
router.include_router(rag_api_router)

base_url = RAGConfig().api_base_url

@router.post("/refresh-vectors")
def refresh_vectors():
    requests.delete(base_url + "/delete-all-vectors")
    requests.delete(base_url + "/delete-all-chunks")
    requests.post(base_url + "/parse")
    time.sleep(10)
    requests.post(base_url + "/create-vectors",json={})
    return {"message": "Vectors refreshed"}