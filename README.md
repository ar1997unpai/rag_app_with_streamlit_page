# Local Document Q&A

A simple chat app for asking questions about your own PDF and TXT documents. It uses Streamlit for the chat page, Ollama for language models, and Qdrant to search document passages.

## First-time setup

### 1. Install and start Ollama

Install [Ollama](https://ollama.com/), then open a terminal and download the two models used by the app:

```powershell
ollama pull embeddinggemma
ollama pull gemma3:4b
```

Keep Ollama running. The app connects to `http://localhost:11434`.

### 2. Start Qdrant

The simplest option is to install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and run this command:

```powershell
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

Keep Qdrant running while using the app. If you already have Qdrant installed, make sure it is reachable at `http://localhost:6333`.

### 3. Install the Python packages

From the project folder, run these commands in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and use that Python executable for the remaining commands.

## Start the app

Whenever you want to use the app:

1. Start Ollama and Qdrant if they are not already running.
2. Open a terminal in the project folder and activate the environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Start the Streamlit chat page:

   ```powershell
   streamlit run frontend/app.py
   ```

   If you did not activate the virtual environment, run:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run frontend/app.py
   ```

4. Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Upload and ask

1. In the left sidebar, choose one or more `.pdf` or `.txt` files.
2. Select **Save and index documents**. The files are saved in `backend/documents/` and indexed in Qdrant.
3. Type a question in the chat box and press Enter.

Each indexing run rebuilds the Qdrant collection from every supported file currently in `backend/documents/`. Uploaded files are local and excluded from Git.

To index files already in `backend/documents/` from PowerShell instead of using the upload button, run this from the project folder:

```powershell
python backend/ingest.py
```

## Folders and files

- `backend/` contains the ingestion, embedding, retrieval, and Ollama chat code.
- `backend/documents/` stores uploaded documents on your computer.
- `frontend/app.py` contains the Streamlit interface.
- `requirements.txt` lists Python dependencies.
