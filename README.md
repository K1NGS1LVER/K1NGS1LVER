# Daniel Paul

**Full-Stack & AI/ML Engineer** | MCA @ Christ University  
Former **Technical Consultant Intern @ Adobe Consulting Services**  
*Building production agentic workflows, on-device RAG systems, and high-throughput backend architecture.*

[LinkedIn](https://linkedin.com/in/daniel-paul-dev) • [Email](mailto:danielpaul150604@gmail.com) • Bengaluru, India

---

### 🚀 Systems & Value Delivered

#### 🔹 Enterprise AI Workflows — Adobe ACS (FinPath)
* **Problem**: Enterprise financial planning workflows suffered from slow sequential tool execution and high latency.
* **How It Helps**: Re-engineered agent execution with **LangGraph** async graph nodes and **Pydantic** schema validation, cutting planning latency by **60%** with 100% type-safe tool execution.
* **Tech**: FastAPI, LangGraph, Supabase, PostgreSQL RLS, React 19

#### 🔹 Local-First Agentic RAG — [docSeek](https://github.com/K1NGS1LVER/docSeek-offline-agentic-RAG)
* **Problem**: Data privacy concerns & cloud API costs block enterprise adoption of document RAG systems.
* **How It Helps**: Delivers a **100% offline**, zero-API-key Corrective RAG pipeline running over local Ollama (`qwen2.5`) with sub-15ms retrieval across **10,000+ indexed pages**.
* **Tech**: LangGraph, FAISS (768-dim), SQLite FTS5, Ollama, Kokoro TTS

#### 🔹 Narrative Intelligence Platform — [ClearNews](https://github.com/K1NGS1LVER/ClearNews)
* **Problem**: Ungrounded LLM summaries obscure news bias and narrative drift over time.
* **How It Helps**: Fuses fine-tuned **BERT** bias classification with **HDBSCAN/UMAP** clustering over 1,000+ daily articles, serving source-grounded answers with real-time SSE streaming.
* **Tech**: BERT, XGBoost, SHAP, pgvector, LangGraph, FastAPI, Redis

#### 🔹 Open Source CLI — [`teacher-sab`](https://github.com/K1NGS1LVER) (npm)
* **Problem**: Cross-agent skill installation friction and frontmatter parsing bugs across AI harness ecosystems.
* **How It Helps**: Published a zero-dependency interactive CLI (`npx teacher-sab install`) supporting 10 AI harnesses with byte-identical skill distribution.
* **Tech**: Node.js, npm registry, YAML parser, E2E CLI testing

---

### 🛠️ Core Engineering Stack

* **AI / ML**: LangGraph, RAG/CRAG, BERT, XGBoost, SHAP, FAISS, pgvector, Ollama, PyTorch
* **Backend**: Python, FastAPI, Node.js, PostgreSQL, Supabase, Redis, Docker
* **Frontend**: TypeScript, React 19, Tailwind CSS, Vite
