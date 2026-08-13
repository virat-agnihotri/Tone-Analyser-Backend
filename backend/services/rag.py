from pathlib import Path
from rag.vector_store import VectorStore

vector_store = VectorStore()
_initialized = False


def _ensure_initial_knowledge():
    global _initialized
    if not _initialized and len(vector_store.documents) == 0:
        knowledge_file = Path(__file__).parent.parent / "rag" / "racing_knowledge.txt"
        if knowledge_file.exists():
            try:
                lines = [line.strip() for line in knowledge_file.read_text().splitlines() if line.strip()]
                vector_store.add_documents(lines)
                print(f"RAG Knowledge Store initialized with {len(lines)} domain chunks.")
            except Exception as e:
                print(f"Warning: Failed to load default racing knowledge: {e}")
        _initialized = True


def add_knowledge(documents: list[str]):
    vector_store.add_documents(documents)


def retrieve_context(query: str, top_k: int = 3) -> list[str]:
    _ensure_initial_knowledge()
    results = vector_store.search(query, top_k)
    return [result["text"] for result in results]