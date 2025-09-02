from sentence_transformers import SentenceTransformer

class EmbeddingModelSingleton:
    _instance = None

    @classmethod
    def get_model(cls, model_name):
        if cls._instance is None:
            cls._instance = SentenceTransformer(model_name)
        return cls._instance

# Usage:
# model = EmbeddingModelSingleton.get_model()