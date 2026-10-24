from pathlib import Path
import sys
from uuid import uuid4
from pypdf import PdfReader
from qdrant_client import models

if __package__:
    from .rag import (
        qdrant,
        COLLECTION_NAME,
        create_collection,
        get_embedding,
        split_text,
    )
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from backend.rag import (
        qdrant,
        COLLECTION_NAME,
        create_collection,
        get_embedding,
        split_text,
    )

DOCUMENTS_DIR = Path(__file__).resolve().parent / "documents"


def extract_text(file_path):
    if file_path.suffix.lower() == ".txt":
        return file_path.read_text(encoding="utf-8")

    if file_path.suffix.lower() == ".pdf":
        reader = PdfReader(str(file_path))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n".join(pages)

    return ""

def ingest_documents(documents_dir=DOCUMENTS_DIR):
    documents_dir = Path(documents_dir)
    documents_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(
        file_path
        for file_path in documents_dir.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in {".txt", ".pdf"}
    )

    if not files:
        raise ValueError("No .txt or .pdf files found in the documents folder.")

    documents = []
    for file_path in files:
        text = extract_text(file_path)
        if text:
            documents.append((file_path, text))
        else:
            print(f"Skipping {file_path.name}: no readable text found.")

    if not documents:
        raise ValueError("No readable text found in the documents folder.")

    # Rebuild the collection only after all files have been read successfully.
    create_collection(recreate=True)
    points = []

    for file_path, text in documents:
        chunks = split_text(text)

        for index, chunk in enumerate(chunks):
            vector = get_embedding(chunk)

            points.append(
                models.PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload={
                        "text": chunk,
                        "source": file_path.name,
                        "chunk": index
                    }
                )
            )

        print(f"Processed {file_path.name}: {len(chunks)} chunks")

    if points:
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True
        )

    print(f"Indexing complete. Stored {len(points)} chunks.")
    return len(points)


if __name__ == "__main__":
    ingest_documents()
