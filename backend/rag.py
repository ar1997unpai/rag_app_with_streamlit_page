import requests
from qdrant_client import QdrantClient,models

OLLAMA_URL = "http://localhost:11434"
QDRANT_URL = "http://localhost:6333"
EMBED_MODEL = "embeddinggemma"
COLLECTION_NAME = "my_documents"

qdrant = QdrantClient(url=QDRANT_URL)

def get_embedding(text):
    response = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json = {
            "model": EMBED_MODEL,
            "input":text
        },
        timeout = 120
    )
    response.raise_for_status()
    data = response.json()
    embeddings = data.get("embeddings")
    if embeddings is None:
        embeddings = data.get("embedding")

    if not embeddings:
        raise ValueError(f"Unexpected Ollama response: {data}")

    # If embeddings is a list of vectors, take first vector
    if isinstance(embeddings, list) and embeddings and isinstance(embeddings[0], list):
        return embeddings[0]

    return embeddings

def split_text(text, chunk_size=300, overlap=50):
    # Character-based chunking for this first version.
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_collection(recreate=False):
    vector_size = len(get_embedding("Check embedding dimensions"))

    if qdrant.collection_exists(COLLECTION_NAME):
        if not recreate:
            return

        qdrant.delete_collection(COLLECTION_NAME)

    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE
        )
    )


def retrieve_context(question, top_k=6):
    if not qdrant.collection_exists(COLLECTION_NAME):
        return []

    query_vector = get_embedding(question)

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True
    )

    return [
        {
            "text": point.payload["text"],
            "source": point.payload["source"],
            "score": point.score
        }
        for point in results.points
    ]
