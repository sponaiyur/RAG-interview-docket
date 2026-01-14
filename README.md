# Project: Interview Docket Generator (Pre-Interview AI Copilot)

## Big Picture (for everyone)

> We are **not** building a hiring system.
> We are **not** deciding pass/fail.
> We are building a tool that helps interviewers ask *better questions faster*.

Everything you build must answer this question:
**“How does this save interviewer time without taking away human control?”**

---

## 👤 Member 1 — Resume Parsing & Structuring

### Handled By: Sharanya
---

### Your responsibility

You take a resume file and convert it into **clean, structured information** that the rest of the system can understand.

Right now, resumes are:

* Messy
* Inconsistent
* Written for humans

Your job is to make them **machine-friendly**.

---

### What you will work on

1. **Resume ingestion**

   * Accept PDF / DOCX resumes
   * Extract raw text reliably

2. **Section identification**
   You must separate text into:

   * Education
   * Skills
   * Projects
   * Experience

3. **Claim extraction**
   From each section, extract:

   * Action statements
     (“Built X”, “Implemented Y”, “Optimized Z”)
   * Tools mentioned
     (“Flask”, “TensorFlow”, “Docker”)

4. **Basic normalization**

   * Remove extra whitespace
   * Standardize bullet points
   * Handle common resume formats

---

### What you will NOT do

* ❌ No machine learning
* ❌ No embeddings
* ❌ No RAG
* ❌ No question generation

If you’re thinking about LLMs, you’ve gone too far.

---

### Output format (non-negotiable)

You must output **JSON**, for example:

```json
{
  "projects": [
    {
      "name": "Smart Parking System",
      "claims": [
        "Designed backend using Flask",
        "Integrated Arduino sensors"
      ],
      "tools": ["Flask", "Arduino"]
    }
  ]
}
```

Other interns should be able to use your output **without asking you questions**.

---

### When you’re done

You are done when:

* The same resume always produces the same structured output
* Another intern can plug your JSON into their code without modification
* A resume with bad formatting does not crash your parser

---

## 👤 Member 2 — Resume Knowledge Base & Retrieval (RAG Core)

### Handled By: Shraddha
---

### Your responsibility

You take structured resume data and make it **searchable by intent**, not keywords.

Example:

* Not “Flask”
* But “backend projects”
* Not “Python”
* But “claims that require validation”

---

### What you will work on

1. **Chunking resume data**

   * Convert resume JSON into meaningful chunks
   * Each chunk should represent a *single idea or claim*

2. **Embedding & storage**

   * Convert chunks into vectors
   * Store them locally (FAISS / Chroma)

3. **Retrieval logic**
   Support queries like:

   * “Retrieve all project-related claims”
   * “Retrieve claims mentioning system design”
   * “Retrieve vague claims”

4. **Explainability**
   Every retrieved chunk must be traceable back to:

   * Resume section
   * Original text

---

### What you will NOT do

* ❌ No internet access
* ❌ No question phrasing
* ❌ No UI
* ❌ No scoring candidates

Your job ends at:
**“Here is the relevant resume content.”**

---

### Output contract

A function like:

```python
retrieve(section="projects", intent="deep") -> list[str]
```

If Person 3 can’t use your output directly, your task is incomplete.

---

### When you’re done

You are done when:

* Retrieval is consistent and fast
* Queries return relevant resume content
* Every retrieved item can be explained

---

## 👤 Member 3 — Interview Question & Logic Engine

### Handled By: Shrey
---

### Your responsibility

You decide **what questions should be asked**, and **why**.

You are designing interview *logic*, not chat responses.

---

### What you will work on

1. **Question taxonomy**
   Design categories:

   * Claim validation
   * Depth probing
   * Trade-off analysis
   * Red-flag clarification

2. **Question templates**
   Example:

   * “You mentioned X — can you explain how Y works?”
   * “What design decisions did you consider here?”

3. **Depth escalation logic**

   * Surface → Intermediate → Deep
   * Based on resume signal quality

4. **Mapping logic**

   * Map resume claims → question types
   * Ensure every question has a justification

---

### What you will NOT do

* ❌ No resume parsing
* ❌ No embeddings
* ❌ No UI
* ❌ No hiring decisions

You are **not** evaluating answers.

---

### Output format

Structured, explainable output:

```json
{
  "claim": "Designed REST API",
  "question": "How did you handle authentication?",
  "reason": "Validates backend depth"
}
```

---

### When you’re done

You are done when:

* Questions are clearly tied to resume claims
* An interviewer understands *why* a question exists
* Questions scale across domains (not just tech)

---

## 👤 Member 4 — Interface & Human Control Layer

### Handled By: Swayam

---

### Your responsibility

You ensure the interviewer:

* Understands the AI’s suggestions
* Can override them
* Never feels replaced

---

### What you will work on

1. **Interview dashboard**

   * Display resume sections
   * Show generated questions
   * Show explanation (“why this question”)


2. **Transparency**

   * Clearly show AI boundaries
   * No hidden automation

---

### What you will NOT do

* ❌ No AI logic
* ❌ No retrieval
* ❌ No parsing

Your focus is **trust and usability**.

---

### When you’re done

You are done when:

* A non-technical interviewer can use the tool
* AI suggestions are clearly distinguishable from human input
* Nothing happens automatically without human action

---