
# FastAPI + LangGraph + ChromaDB (RAG)

## Python Environment Setup

It is recommended to use a virtual environment to manage dependencies and avoid conflicts:

### 1. Create a virtual environment
```bash
python -m venv .venv
```

### 2. Activate the virtual environment
- **macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows:**
  ```bash
  .venv\Scripts\activate
  ```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment variables
Copy the example environment file and set your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY or set EMBEDDING_BACKEND=local
```

## Startup

### Option 1: Manual (in two terminals)

**Terminal 1: Start FastAPI backend**
```bash
uvicorn app.main:app --reload
```

**Terminal 2: Start Streamlit UI**
```bash
streamlit run app/streamlit_app.py
```

---

### Option 2: Automated (using Honcho)

**Start both FastAPI and Streamlit together:**
```bash
honcho start
```

**To run only one service:**
- FastAPI backend:  
  ```bash
  honcho run web
  ```
- Streamlit UI:  
  ```bash
  honcho run ui
  ```

---
## Crawl Using Postman

You can use Postman to trigger a crawl:

1. **Set method:** `POST`
2. **URL:** `http://localhost:8000/crawl`
3. **Headers:**  
   - `Content-Type: application/json`
4. **Body (raw, JSON):**
   ```json
   {
     "root_url": "https://quotes.toscrape.com/",
     "max_pages": 100
   }
   ```
5. **Send** the request to start crawling the site.


## Usage

1. Open [http://localhost:8501](http://localhost:8501) in your browser for the Streamlit UI.
4. Ask questions based on your crawled knowledge base.

---

## Environment

- Python 3.10+
- FastAPI
- Uvicorn
- Streamlit
- ChromaDB
- LangGraph
- LangChain
- OpenAI API (or local embedding backend)

---
