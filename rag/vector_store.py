import faiss
import numpy as np
from rag.embeddings import create_embeddings


class VectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []

    def add_documents(self, documents: list[str]):
        if not documents:
            return

        valid_docs = [doc.strip() for doc in documents if doc and doc.strip()]
        if not valid_docs:
            return

        embeddings = create_embeddings(valid_docs)
        embeddings = np.asarray(embeddings, dtype="float32")

        self.index.add(embeddings)
        self.documents.extend(valid_docs)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if not self.documents or self.index.ntotal == 0 or not query.strip():
            return []

        query_embedding = create_embeddings([query])
        query_embedding = np.asarray(query_embedding, dtype="float32")

        k = min(top_k, len(self.documents))
        distances, indices = self.index.search(query_embedding, k)

        results = []
        if len(indices) > 0:
            for index, distance in zip(indices[0], distances[0]):
                if index < 0 or index >= len(self.documents):
                    continue
                results.append({
                    "text": self.documents[index],
                    "distance": float(distance)
                })

        return results