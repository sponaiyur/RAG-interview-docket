# System Components Deep Dive

This document explains the internal logic, algorithms, and prompt engineering behind the three core components of RAG Interview Docket.

---

## 1. The Resume Parser (`core.parser`)

**Goal**: Convert unstructured PDF text into a semi-structured JSON format that separates Skills, Experience, and Projects.

### How it works
The parser does not use an LLM (to keep it fast and deterministic). Instead, it uses **Heuristic Section Parsing**.

#### A. Text Extraction
We use `pdfplumber` to extract text line-by-line. This is more reliable than `PyPDF2` for maintaining layout order.

#### B. Section Identification
We iterate through the lines and check against a dictionary of **Section Synonyms**.
```python
SECTION_SYNONYMS = {
    "experience": ["work experience", "employment history", ...],
    "projects": ["academic projects", "technical projects", ...],
    "skills": ["technical skills", "technologies", ...]
}
```
When a line matches a synonym, we switch the "context" to that section.

#### C. Experience Parsing Logic
The experience parser is a state machine that handles:
1.  **Role/Company Detection**: Uses regex to identify lines that look like a Role (e.g., "Software Engineer") vs a Company (often followed by a date).
2.  **Date Parsing**: A robust regex `DATE_PATTERN` identifies durations (e.g., "Jan 2020 - Present", "05/2021").
3.  **Bullet Point Filtering**: Lines starting with regex `^[•\-]` are treated as "Claims".

---

## 2. The Agentic Chunker (`core.chunker`)

**Goal**: Re-organize the linear resume into **Skill-Based Chunks**. This is the "RAG" part—we want to retrieve only the relevant parts of the resume for a specific topic.

### How it works
This component follows a 2-step LLM pipeline.

#### Step 1: Skill Extraction
First, we look at the **Job Description (JD)** to find what matters.
-   **Prompt**: `TASK: Extract technical skills from a Job Description.`
-   **Input**: The raw JD text.
-   **Output**: `["Python", "Kubernetes", "System Design"]`

#### Step 2: Semantic Chunking
We feed the **Parsed Resume** and the **Target Skills** into a powerful LLM (Groq/Llama3-70b).
-   **Prompt Strategy**: "Look for SEMANTIC matches."
    -   *Implicit Matching*: If the resume says "Built a REST API", the LLM knows to link this to the "Backend" skill.
    -   *Evidence Aggregation*: It pulls claims from Project A and Experience B if they both relate to "Python".
-   **Output Schema**:
    ```json
    {
      "focus_skill": "Machine Learning",
      "chunk_summary": "Candidate has 2 years of experience with Scikit-Learn...",
      "claims": [ ... ]
    }
    ```

---

## 3. The Question Engine (`core.question_engine`)

**Goal**: Generate high-quality interview questions from specific claims.

### How it works
This uses a **Local LLM (Ollama/Qwen2.5)** to ensure privacy and zero cost per question.

#### A. Classification
Before generation, we run a keyword heuristic to tag the claim type:
-   `optimize`, `reduced` -> **OPTIMIZATION**
-   `design`, `architect` -> **DESIGN**
-   `built`, `implemented` -> **IMPLEMENTATION**

#### B. Structured Prompting
We do not ask the LLM to "just generate questions." We force it to fill specific **Cognitive Slots**:

1.  **Clarification**: Checks for scope/vague wording ("What did you mean by...?").
2.  **Base Overview**: Checks basic understanding ("How does it work?").
3.  **Depth (Trade-off)**: Probes decision making ("Why X instead of Y?").
4.  **Depth (Failure)**: Probes resilience ("What happens if it fails?").
5.  **Challenge**: Hypothetical scenarios ("How would you scale this to 100x?").

#### C. Parallel Execution
Since `ollama run` is a blocking subprocess call, we wrap it in a `ThreadPoolExecutor`.
-   The Controller splits the Chunks into individual Claims.
-   It spawns 3 worker threads.
-   Each thread runs an independent LLM session.
-   Results are `yielded` back to the UI immediately for a streaming effect.

---

## 4. Pipeline Orchestration (`core.pipeline_client`)
This simple module acts as the "glue". It replaces the need for a Flask/FastAPI backend.
-   It imports the `Parser`, `Chunker`, and `Generator` classes directly.
-   It handles the `tempfile` logic for PDF uploads (since `pdfplumber` needs a file path).
-   It manages the generator stream.
