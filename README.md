# Email-RAG-System--AI-Chat-

An AI-powered email intelligence system built using the Enron Email Dataset. The system allows users to ask natural-language questions about the email knowledge base and receive AI-generated answers with relevant sources and confidence information.

## Features

- Natural-language email question answering
- RAG-based contextual responses
- Hybrid FAISS + BM25 retrieval
- Local LLM inference using Ollama
- Source-aware answers with confidence scores
- Entity intelligence
- Communication hub analysis
- MongoDB-based email and chunk storage
- React-based interactive interface
- FastAPI REST and WebSocket APIs

## Technology Stack

- **Frontend:** React.js
- **Backend:** FastAPI, Python
- **Database:** MongoDB
- **Vector Search:** FAISS
- **Keyword Search:** BM25
- **Embeddings:** all-MiniLM-L6-v2
- **LLM:** Ollama with a Llama-based model
- **Communication:** REST API and WebSocket
- **Dataset:** Enron Email Dataset

## System Overview

The system processes the Enron Email Dataset and stores the email data in MongoDB. Emails are divided into smaller chunks and converted into vector embeddings using `all-MiniLM-L6-v2`.

For user questions, the system performs hybrid retrieval using FAISS semantic search and BM25 keyword search. Retrieved information is passed to the RAG service, which builds the context and sends it to the locally running Ollama LLM. The generated answer is returned to the React frontend along with relevant sources and confidence information.

The system also provides additional email intelligence features such as entity analysis and communication hub detection.

## Project Structure

```text
Enron-Email-Dataset-AI-Chat-System/
│
├── backend/
│   ├── app/
│   │   ├── database/
│   │   ├── embeddings/
│   │   ├── insights/
│   │   ├── rag/
│   │   ├── routes/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── vector_index.faiss
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
└── README.md
```

## How to Run

Follow the steps below to run the complete application on Windows.

### 1. Prerequisites

Install the following:

- Python 3.12
- Node.js and npm
- MongoDB
- Ollama
- Git

Verify the installations:

```powershell
python --version
node --version
npm --version
mongod --version
ollama --version
git --version
```

### 2. Clone the Repository

Open PowerShell:

```powershell
git clone https://github.com/yashparab398-jpg/Enron-Email-Dataset-AI-Chat-System.git
cd Enron-Email-Dataset-AI-Chat-System
```

### 3. Start MongoDB

Make sure MongoDB is installed and running.

If MongoDB is installed as a Windows service:

```powershell
net start MongoDB
```

The application requires the processed Enron dataset to be available in MongoDB, including the required email and chunk collections.

### 4. Start Ollama

Open a new PowerShell terminal.

Start the Ollama server:

```powershell
ollama serve
```

Keep this terminal running.

Open another PowerShell terminal and check the installed models:

```powershell
ollama list
```

If the model required by the project is not installed:

```powershell
ollama pull <model-name>
```

The model name must match the model configured in the backend.

### 5. Set Up the Backend

Open another PowerShell terminal.

Go to the backend directory:

```powershell
cd Enron-Email-Dataset-AI-Chat-System\backend
```

Create a Python virtual environment:

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
pip install -r requirements.txt
```

### 6. Start the FastAPI Backend

Make sure the virtual environment is activated.

Start the backend:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Keep this terminal running.

### 7. Set Up the Frontend

Open another PowerShell terminal.

Go to the frontend directory:

```powershell
cd Enron-Email-Dataset-AI-Chat-System\frontend
```

Install the frontend dependencies:

```powershell
npm install
```

### 8. Start the React Frontend

From the `frontend` directory, run:

```powershell
npm start
```

The frontend will normally run at:

```text
http://localhost:3000
```

Open this address in your browser.

## Complete Startup

The application requires the following services to be running simultaneously.

### Terminal 1 — MongoDB

```powershell
net start MongoDB
```

### Terminal 2 — Ollama

```powershell
ollama serve
```

### Terminal 3 — Backend

```powershell
cd Enron-Email-Dataset-AI-Chat-System\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Terminal 4 — Frontend

```powershell
cd Enron-Email-Dataset-AI-Chat-System\frontend
npm start
```

### Open the Application

After all services are running, open:

```text
http://localhost:3000
```

## Limitations

- Retrieval quality depends on the quality of the stored email chunks and embeddings.
- Local LLM response speed depends on available CPU/GPU resources.
- Ollama must be running locally for AI-generated responses.
- The current system is designed around the Enron Email Dataset.
- Large-scale deployment would require more optimized indexing and infrastructure.
- Entity and communication analysis currently operates on the available processed dataset.
- MongoDB must contain the required processed data before the application can provide complete results.

## Future Scalability

The system can be extended with:

- Larger and more powerful embedding models
- Advanced reranking models
- Distributed vector databases such as Milvus, Qdrant, or Pinecone
- Distributed MongoDB deployment
- GPU-based LLM inference
- Larger and domain-specific language models
- Multi-dataset and multi-tenant support
- Advanced entity relationship graphs
- Real-time email ingestion
- Authentication and role-based access control
- Cloud deployment and containerization using Docker
- Horizontal scaling of the FastAPI backend
- Improved caching for faster responses
- Monitoring, logging, and performance analytics

## Key Components

### Hybrid Retrieval

The retrieval system combines:

- **FAISS** for semantic similarity search
- **BM25** for keyword-based search
- **Term matching** for additional lexical relevance
- **Phrase matching** for important multi-word concepts

This combination improves retrieval across both natural-language questions and exact email terminology.

### Retrieval-Augmented Generation

The RAG pipeline retrieves relevant email chunks before generating an answer. This helps the LLM ground its responses in the Enron email knowledge base instead of relying only on its pretrained knowledge.

### Entity Intelligence

The entity intelligence module identifies frequently occurring email addresses and entities across the processed dataset.

### Communication Hubs

The communication hub analysis identifies highly active email participants and relationships between senders and recipients.

## License

This project is provided for educational and research purposes.

The Enron Email Dataset is subject to its respective dataset licensing and usage terms. Users are responsible for complying with the applicable terms when using or redistributing the dataset.

---

## Author

**Yash Parab**

**Repository:** Enron-Email-Dataset-AI-Chat-System
