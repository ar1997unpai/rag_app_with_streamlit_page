from pathlib import Path
import sys

import streamlit as st
import requests
from pypdf.errors import PdfReadError
from qdrant_client.http.exceptions import ApiException, ResponseHandlingException

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.ingest import DOCUMENTS_DIR, ingest_documents
from backend.promptResponse import post_request
from backend.rag import retrieve_context


st.set_page_config(page_title="Document Q&A")
st.title("Document Q&A")
st.write("Upload PDF or TXT documents, index them, and ask questions about their contents.")

with st.sidebar:
    st.header("Your documents")
    uploads = st.file_uploader(
        "Choose one or more PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True,
    )

    if st.button("Save and index documents", disabled=not uploads):
        with st.status("Saving and indexing documents...", expanded=True) as status:
            try:
                status.write("Saving uploaded files to `backend/documents/`.")
                DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
                for upload in uploads:
                    destination = DOCUMENTS_DIR / Path(upload.name).name
                    destination.write_bytes(upload.getvalue())

                status.update(
                    label="Creating embeddings and indexing in Qdrant...",
                    state="running",
                )
                chunk_count = ingest_documents()
            except (
                OSError,
                ValueError,
                PdfReadError,
                requests.RequestException,
                ApiException,
                ResponseHandlingException,
            ) as error:
                status.update(label="Document indexing failed", state="error")
                st.error(f"Could not index the documents: {error}")
            else:
                status.update(
                    label=f"Indexed {chunk_count} text chunks.",
                    state="complete",
                    expanded=False,
                )

    if DOCUMENTS_DIR.exists():
        stored_files = sorted(
            file.name
            for file in DOCUMENTS_DIR.iterdir()
            if file.is_file() and file.suffix.lower() in {".txt", ".pdf"}
        )
        if stored_files:
            st.caption("Files saved locally:")
            for filename in stored_files:
                st.write(f"- {filename}")
        else:
            st.caption("No documents have been uploaded yet.")
    else:
        st.caption("No documents have been uploaded yet.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.caption("Sources: " + ", ".join(message["sources"]))

if question := st.chat_input("Ask a question about your documents"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            documents = retrieve_context(question)
            context = "\n\n".join(
                f"Source: {document['source']}\n{document['text']}"
                for document in documents
            )
            if not context:
                context = "No relevant documents were retrieved."

            answer = post_request(question, context)["message"]["content"]
        except (
            OSError,
            ValueError,
            requests.RequestException,
            ApiException,
            ResponseHandlingException,
        ) as error:
            st.error(f"Could not answer the question: {error}")
        else:
            sources = sorted({document["source"] for document in documents})
            st.markdown(answer)
            if sources:
                st.caption("Sources: " + ", ".join(sources))
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": sources}
            )
