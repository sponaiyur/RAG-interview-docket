# 🧠 RAG Interview Docket

**RAG Interview Docket** is a local-first, AI-powered assistant for technical interviewers. It helps you ask better questions by analyzing a candidate's resume against the Job Description (JD) and generating targeted, intent-driven questions.

> **Privacy Focused**: resume parsing and question generation happen entirely on your machine.

---

## 🚀 Features

-   **📄 Resume Parsing**: Automatically extracts experience, skills, and projects from PDF resumes.
-   **🔍 Semantic Chunking**: Intelligently groups resume claims by skill (e.g., "Python", "System Design") using Cloud APIs.
-   **🤖 Local Question Generation**: Generates 7+ types of interview questions (Clarification, Depth, Trade-offs) using a local LLM.
-   **⚡ Real-Time Streaming**: Questions appear instantly as they are generated using parallel processing.
-   **💡 Explainability**: Every question is linked to the specific resume claim it targets.

---

## 🛠️ Architecture Overview

The system operates in a 3-stage pipeline:

1.  **Ingestion**: `Streamlit UI` -> `PDF Parser` -> `Structured JSON`
2.  **Chunking**: `Structured JSON` + `JD` -> `Groq API` -> `Skill-based Chunks`
3.  **Generation**: `Chunks` -> `Local LLM (Ollama)` -> `Interview Questions`

For a deep dive into the code structure, see [ARCHITECTURE.md](architecture.md).

---

## 📦 Installation

### Prerequisites
1.  **Python 3.10+**
2.  **[Ollama](https://ollama.ai/)** installed and running.
3.  **Groq API Key** (for high-speed chunking).

### Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/RAG-interview-docket.git
    cd RAG-interview-docket
    ```

2.  **Install Dependencies**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    ```

4.  **Pull the Local Model**:
    ```bash
    ollama pull qwen2.5:latest
    ```
    *(You can change the model in `core/question_engine/llm_utils.py` if needed)*

---

## ▶️ Usage

1.  **Start the App**:
    ```bash
    streamlit run app.py
    ```

2.  **Workflow**:
    -   **Step 1**: Upload a Candidate's Resume (PDF).
    -   **Step 2**: Paste the Job Description (JD) text.
    -   **Step 3**: Select the Interview Stage (Screening, Technical, etc.).
    -   **Step 4**: Click **Generate Questions**.
    -   **Step 5**: Watch as questions stream in real-time!

---

## 🧩 Project Structure

```bash
RAG-interview-docket/
├── app.py                  # Streamlit Entry Point
├── architecture.md         # Detailed System Architecture
├── core/
│   ├── chunker/            # Semantic analysis logic
│   ├── parser/             # PDF parsing logic
│   ├── question_engine/    # Local LLM generation logic
│   └── pipeline_client.py  # Orchestrator
├── ui/                     # UI Components
└── data/                   # Storage for parsed resumes
```

---

## 🤝 Contributing

1.  Fork the repo.
2.  Create a feature branch.
3.  Submit a Pull Request.

---

## 📄 License
MIT License.