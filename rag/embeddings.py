import os
from sentence_transformers import SentenceTransformer

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        print(f"Loading embedding model: {model_name}")
        is_offline = os.getenv("HF_HUB_OFFLINE", "0") in ("1", "true", "True")

        # 1. Try loading from local Hugging Face cache first
        try:
            _model = SentenceTransformer(model_name, local_files_only=True)
            print(f"Loaded embedding model from local cache.")
            return _model
        except Exception as local_err:
            if is_offline:
                print(
                    "Unable to reach Hugging Face Hub.\n"
                    "This may be a DNS/network problem rather than an authentication problem.\n"
                    "Please verify that huggingface.co can be resolved and reached."
                )
                raise RuntimeError(
                    f"Embedding model '{model_name}' is not available in local cache and offline mode is active."
                ) from local_err
            print(f"Embedding model '{model_name}' not fully cached. Attempting online load...")

        # 2. Try online load if not cached
        try:
            _model = SentenceTransformer(model_name, local_files_only=False)
            print(f"Successfully downloaded and loaded embedding model '{model_name}'.")
        except Exception as net_err:
            print(
                "Unable to reach Hugging Face Hub.\n"
                "This may be a DNS/network problem rather than an authentication problem.\n"
                "Please verify that huggingface.co can be resolved and reached."
            )
            raise RuntimeError(
                f"Embedding model '{model_name}' is not cached and Hugging Face (huggingface.co) "
                f"could not be reached: {net_err}"
            ) from net_err

    return _model

def get_embeddings(texts: list[str]) -> list:
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()

# Export alias for compatibility
create_embeddings = get_embeddings