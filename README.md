# Atlas

**An intelligent knowledge drive — files and folders, with a semantic layer underneath.**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-server-009688?style=flat-square&logo=fastapi&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-vector%20store-DC244C?style=flat-square&logo=qdrant&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/status-Phase%2001%20·%20Plan%2001-yellow?style=flat-square)
![License](https://img.shields.io/badge/license-unlicensed-lightgrey?style=flat-square)

Atlas is being built RAG-first and interview-defensible: every pipeline
stage is implemented, verified, and explainable before the next one
starts. No shortcuts, no unexplained logic.

---

## 📍 Status

| Stage                               | State          |
| ----------------------------------- | -------------- |
| Upload · text extraction · chunking | ✅ Done        |
| Embedding · vector storage (Qdrant) | ⬜ Not started |
| Retrieval                           | ⬜ Not started |
| Generation · streaming · citation   | ⬜ Not started |
| Client UI                           | ⬜ Not started |

Only what's checked off above actually exists — this is a build log, not
a roadmap dressed up as a feature list.

---

## 🚀 Run the stack

```bash
docker compose up --build
```

- API → `http://localhost:8000`
- Qdrant → `http://localhost:6333` (running, not yet wired into the app)

Stop everything:

```bash
docker compose down
```

Liveness check:

```bash
curl -i http://localhost:8000/system/health
```

---

## 📤 Upload a file

```bash
curl -X POST http://localhost:8000/documents/upload -F "file=@./samples/example.pdf"
curl -X POST http://localhost:8000/documents/upload -F "file=@./samples/example.md"
```

**Rejection cases** (unsupported type, empty file):

```bash
curl -i -X POST http://localhost:8000/documents/upload -F "file=@./samples/example.txt"
curl -i -X POST http://localhost:8000/documents/upload -F "file=@./samples/empty.md"
```

---

## 🧪 Run tests

```bash
python -m pip install -r server/requirements.txt
python -m unittest discover -s server/tests -v
```

PDF tests generate a small standards-compliant PDF in memory — no
external fixture dependency, `pdfplumber` reads it exactly as it would
a real upload.

---

## 🗺️ Build plans

Full architecture decisions, phase/plan breakdowns, and Codex prompts
live in [`prompts/`](./prompts) and [`AGENTS.md`](./AGENTS.md).
