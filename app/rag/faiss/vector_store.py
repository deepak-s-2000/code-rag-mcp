import faiss
import numpy as np
from app.config import RAGConfig
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, dimension: int, M=32):
        self.dimension = dimension
        self.index = faiss.IndexHNSWFlat(dimension, M, faiss.METRIC_INNER_PRODUCT)
        self.faiss_filepath = RAGConfig().faiss_filepath
        
    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.clip(norms, 1e-10, None)
    
    async def clear_index(self):
        self.index.reset()
        logger.info("Cleared FAISS index.")

    async def load_index(self):
        if os.path.exists(self.faiss_filepath):
            self.index = faiss.read_index(self.faiss_filepath)
            logger.info(f"Loaded FAISS index from {self.faiss_filepath}.")
        else:
            logger.warning(f"FAISS index file not found: {self.faiss_filepath}")

    async def add_vectors(self, vectors: np.ndarray):
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        vectors = self._normalize(vectors)
        logger.info(f"Adding {vectors.shape[0]} vectors to FAISS index.")
        self.index.add(vectors)
        

    async def search(self, query_vector: np.ndarray, k: int = 5) -> tuple[np.ndarray, np.ndarray]:
        await self.load_index()
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        query_vector = self._normalize(query_vector)
        distances, indices = self.index.search(query_vector, k)
        return distances, indices
    
    async def save_index(self):
        # if os.path.exists(self.faiss_filepath):
        #     os.remove(self.faiss_filepath)
        faiss.write_index(self.index, self.faiss_filepath)
        logger.info(f"Saved FAISS index to {self.faiss_filepath}.")
        # if os.path.exists(self.faiss_filepath):
        # # Load existing index
        #     existing_index = faiss.read_index(self.faiss_filepath)
        # # Add vectors from self.index to existing_index
        # # Get all vectors from self.index
        #     total = self.index.ntotal
        #     if total > 0:
        #         logger.info(f"Saving {total} vectors to existing index.")
        #     # Extract all vectors from self.index
        #         vectors = self.index.reconstruct_n(0, total)
        #         existing_index.add(vectors)
        #     faiss.write_index(existing_index, self.faiss_filepath)
        # else:
        #     faiss.write_index(self.index, self.faiss_filepath)