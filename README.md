# Atlas

**An intelligent knowledge drive — files and folders, with a semantic layer underneath.**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-server-009688?style=flat-square&logo=fastapi&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-vector%20store-DC244C?style=flat-square&logo=qdrant&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/status-Phase%2001%20·%20Plan%2002-yellow?style=flat-square)
![License](https://img.shields.io/badge/license-unlicensed-lightgrey?style=flat-square)

Atlas is being built RAG-first and interview-defensible: every pipeline
stage is implemented, verified, and explainable before the next one
starts. No shortcuts, no unexplained logic.

---

## 📍 Status

| Stage                               | State                                                         |
| ----------------------------------- | ------------------------------------------------------------- |
| Upload · text extraction · chunking | Local tests and live fixtures pass; extraction gap documented |
| Embedding · vector storage (Qdrant) | Verified locally and with Docker uploads                      |
| Retrieval                           | ⬜ Not started                                                |
| Generation · streaming · citation   | ⬜ Not started                                                |
| Client UI                           | ⬜ Not started                                                |

Only what's marked implemented above actually exists — this is a build log, not
a roadmap dressed up as a feature list.

Plan 02 remains in progress: the Qdrant-only database health endpoint is
still deferred. Docker startup and Markdown/full-PDF upload storage
checks pass, including the unavailable-database error path.

Extraction caveat: the local environment and Docker currently install
different Docling versions. A sparse PDF produced different chunks and
omitted an isolated line in Docker; broader Plan 01 manual verification
remains pending. Details are in the
[Plan 02 context](prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_CONTEXT.md).

---

## 🚀 Run the stack

```bash
cd server
# Create .env from .env.example if it does not already exist.
docker compose --env-file .env -f docker-compose.yml up --build -d
```

- API → `http://localhost:8080` (default example PORT; use your .env value)
- Qdrant → `http://localhost:6333` (wired into upload storage)
- Wait for `Upload startup ready` in server logs before sending requests.
- The build caches Docling and BGE-M3 weights; startup prepares the model
  and collection before accepting uploads. Build failure means these
  runtime checks have not run.

Stop everything:

```bash
docker compose --env-file .env -f docker-compose.yml down
```

Liveness check:

```bash
curl -i http://localhost:8080/system/health
```

---

## 📤 Upload a file

```bash
curl -X POST http://localhost:8080/documents/upload -F "file=@/path/to/example.pdf"
curl -X POST http://localhost:8080/documents/upload -F "file=@/path/to/example.md"
```

Use `curl.exe` in Windows PowerShell and replace the example paths.
Uploads return chunks and additionally store one Qdrant point per chunk.
Stored payloads retain contextualized `text` and raw `display_text`;
every upload gets a new internal UUID, with no deduplication.

Docling supports PDF, DOCX, PPTX, XLSX, Markdown, text, HTML, CSV, and
PNG/JPG/JPEG/TIFF/BMP/WebP images. Chunking uses the BGE-M3 tokenizer;
embedding uses dense-only BGE-M3 vectors (1024 dimensions, cosine).

**Rejection cases** (unsupported type, empty file):

```bash
curl -i -X POST http://localhost:8080/documents/upload -F "file=@/path/to/example.zip"
curl -i -X POST http://localhost:8080/documents/upload -F "file=@/path/to/empty.md"
```

---

## 🧪 Run tests

From `server/`, using the project's activated virtual environment:

```bash
python -m pip install -r requirements.txt -r tests/requirements.txt
python -m tests.run
```

The runner prepares the real embedder and temporary in-memory Qdrant,
performs two timed HTTP uploads, then runs all 21 tests. Bare discovery
does not prepare the startup services required by older upload tests.
PDF fixtures use ReportLab and are parsed by Docling, not pdfplumber.
The first run may download model weights; local tests do not alter your
Docker Qdrant data.

For beginner-friendly setup and live point/payload checks, see the
[Plan 02 manual](prompts/PHASE_01/PLAN_02/PHASE_01_PLAN_02_MANUAL.md).

---

## 🗺️ Build plans

Full architecture decisions, phase/plan breakdowns, and Codex prompts
live in [`prompts/`](./prompts). Repository-wide instructions live in
[`AGENTS.md`](./AGENTS.md), with inherited frontend rules in
[`client/AGENTS.md`](./client/AGENTS.md) and backend rules in
[`server/AGENTS.md`](./server/AGENTS.md). Read root instructions and each applicable
scoped file; detailed RAG contracts remain in the [RAG skill](./.agents/skills/rag/SKILL.md).
