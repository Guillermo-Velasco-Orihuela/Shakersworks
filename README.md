# ShakersWorks RAG + Recommender

**Brief Summary**  
This project delivers a dual-purpose AI assistant:  
1. A **Retrieval-Augmented Generation (RAG)** chat interface over a set of Markdown documentation (API guides, billing, features, etc.), powered by OpenAI embeddings and a Chroma vector store.  
2. A **Talent Recommendation** system that accepts free-form job requests (e.g. “I need an Android developer with 8 years of experience”) and returns the best matches from a seeded SQLite database, using vector similarity search.  

Under the hood the backend uses FastAPI, Redis caching, Prometheus/Grafana monitoring, and all components are containerized via Docker Compose. The frontend is built with Streamlit for an interactive chat UI.

---

## File Structure
```bash
├── README.md
├── backend
│   ├── .env
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── prometheus_config/
│   ├── grafana/
│   ├── chroma_db/
│   ├── data/*.md
│   ├── shakers.db
│   ├── requirements.txt
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   └── scripts/
├── frontend
│   └── app.py
└── environment.yml
```


---

## Features

- **FastAPI Backend**  
  - **RAG Q&A** (`POST /query`) with Redis caching, Prometheus metrics, and OpenAI LLM.  
  - **Talent Recommendations** (`POST /recommend`) via vector similarity over talent_profiles.  
  - **Admin** (`POST /reload-index`) to re-ingest Markdown at runtime.  
  - **Metrics** (`GET /metrics`) in Prometheus format.

- **Vector Store**  
  - Chroma (DuckDB+Parquet) for persistent embedding search.  
  - Embeddings generated via OpenAI Embeddings API.

- **Caching & Monitoring**  
  - Redis for 5-minute caching of RAG results.  
  - Prometheus counters/histograms for cache hits, misses, LLM calls, request latency.  
  - Grafana dashboard pre-configured for metrics visualization.

- **Streamlit Frontend**  
  - Interactive chat with sidebar mode switch: **Chat (RAG)** vs. **Recommendations**.

- **Containerization**  
  - Docker Compose orchestration for Redis, Prometheus, Grafana.

---

## Prerequisites

- Docker Desktop  
- Python 3.10+  
- Conda (Miniconda or Anaconda)  
- `streamlit` (installed in your Conda environment)  
- An OpenAI API key  

---

## Project Setup

1. **Create and activate the Conda environment**  
   From the project root, run:  

   ```bash
   conda env create -f environment.yml
   conda activate ShakersworksCase
   ```

2. **Configure environment**  
   In `backend/.env` set your openai key, please always make sure to not share your key and set a low limit of possible usage cost.  

   ```env
   OPENAI_API_KEY=sk-…
   VECTOR_STORE_URL=./chroma_db
   DATABASE_URL=sqlite:///./shakers.db
   REDIS_URL=redis://localhost:6379/0
   ```

3. **Launch infrastructure**

    Please make sure you have installed Docker Desktop and its open when executing the docker compose up

    ```bash
    cd backend
    docker-compose up -d
    ```

4. **Start the backend**

    ```bash
    cd backend
    uvicorn app.main:app --reload
    ```

5. **Run frontend**

    ```bash
    cd ../frontend
    streamlit run app.py

    ```


## Usage

- **Chat (RAG)**
    Ask questions about the ingested Markdown docs.
    - **Example prompt:** What are the different roles and permissions available when inviting collaborators in Shakers?

- **Recommendations**
    Enter a job description (e.g. “I need an Android developer with 8 years of experience”) and receive top candidate matches.
    - **Example prompt:** I need an Android developer with 8 years of experience



## Monitoring & Grafana Dashboard

1. **Log in to Grafana**  
   - URL: `http://localhost:3000`  
   - User: `admin` / Password: `admin`  

2. **Add the Prometheus data source**  
   - Navigate to **Configuration → Data Sources**  
   - Click **Add data source** and select **Prometheus**  
   - Set **URL** to `http://host.docker.internal:9090`  
   - Click **Save & Test** to verify connectivity  

3. **Import the pre-built dashboard**  
   - Go to **Create → Import**  
   - Upload the file `backend/grafana/dashboards/dashboard.json`  
   - Select your Prometheus data source and click **Import**  

4. **View the dashboard**  
   - Navigate to **Dashboards → Manage**  
   - Click on **Shakers Full Metrics** to open the dashboard
