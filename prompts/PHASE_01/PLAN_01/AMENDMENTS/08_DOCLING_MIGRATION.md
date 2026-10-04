# Amendment 08 — Docling Migration (Extraction + Chunking Replaced)

The largest single amendment: replaces pdfplumber + manual tiktoken
chunking entirely with Docling's DocumentConverter + HybridChunker.
Expands accepted upload formats from {.pdf, .md} to 8 format categories
including OCR'd images. Preceded by a full research/debate on
LangChain+Docling (rejected LangChain) and Docling+BGE-M3+Qdrant
(accepted), documented in chat, not reproduced here.

````
CONTEXT

Amendment to PHASE_01_PLAN_01's existing code, staying on the
phase-01/plan-01 branch (this replaces the extraction/chunking
implementation, not a new pipeline stage — no new plan/branch per
AGENTS.md). Before writing any code, review current git state (branch,
other branches, recent commits) per AGENTS.md — do not commit, edit,
delete, or switch branches under any circumstance.

Read AGENTS.md and the rag skill in full before starting — both have
been fully updated with the Docling-based contract this prompt
implements. This replaces pdfplumber + manual tiktoken-based chunking
entirely. Embedding/Qdrant storage remains PLAN_02 and is explicitly out
of scope here — do not touch anything embedding-related.

OBJECTIVE

Replace the current extraction+chunking implementation with Docling's
DocumentConverter + HybridChunker, per the rag skill's contract. Expand
accepted upload formats from {.pdf, .md} to the full locked set. Update
the Chunk/response schemas to carry the richer metadata Docling
provides. Update the Dockerfile to pre-warm the new, heavier model
caches instead of tiktoken's.

CONSTRAINTS

Dependencies:
- Remove: pdfplumber, tiktoken
- Add: docling, rapidocr_onnxruntime, transformers
- Update requirements.txt (or pyproject.toml, whichever this project
  uses) accordingly.

Docling pipeline configuration:
```python
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = RapidOcrOptions(backend="onnxruntime")

converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)
````

Adapt as needed for the actual Docling version installed and for
non-PDF formats — this is a reference showing intent (standard pipeline

- OCR via RapidOCR, no VLM pipeline), not a literal drop-in. Verify
  against current Docling docs if the API shape differs.

Chunking configuration:

```python
from docling.chunking import HybridChunker
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-m3")
chunker = HybridChunker(tokenizer=tokenizer, max_tokens=500, merge_peers=True)

for chunk in chunker.chunk(dl_doc):
    text = chunker.contextualize(chunk)   # canonical text — heading-enriched, not raw chunk.text
```

Canonical chunk text is the `contextualize()` output, not raw
`chunk.text` — this is what PLAN_02 will embed.

Accepted upload formats (replacing the current {.pdf, .md} check):
.pdf, .docx, .pptx, .xlsx, .md, .txt, .html, .csv, and images (.png,
.jpg/.jpeg, .tiff, .bmp, .webp). Update the router's validation and the
ApiError message accordingly. Do not add audio/video or any format
outside this list.

Schema changes (schemas/pipeline.py, schemas/documents.py):

- Extend the existing Chunk class with new fields sourced from
  Docling's chunk.meta: page, heading, section (single-word names, per
  project naming convention — not page_number/chunk_heading etc.). Keep
  existing fields (id, text, index, count) as-is, just extend.
- Extend ResponseChunk to expose the same new fields.
- These new fields may be None/optional where Docling's metadata
  doesn't provide them for a given format (e.g. a .txt file has no
  headings or pages) — handle this, don't force a value.

Dockerfile:

- Remove the tiktoken cache pre-warm step
  (TIKTOKEN_CACHE_DIR / the `tiktoken.get_encoding` RUN line).
- Add an equivalent pre-warm step for the new, heavier models: Docling's
  layout/table/OCR models and the BAAI/bge-m3 tokenizer, so these
  download at build time, not on first request. Determine the correct
  cache directory/environment variables for Docling and
  transformers/HuggingFace (e.g. HF_HOME) from current documentation —
  don't guess the variable name.
- Expect and accept a meaningfully larger image and slower build — this
  is a known, intentional trade-off, not something to minimize or work
  around.

Per AGENTS.md: SUMMARY and MANUAL updates must be short bullet points,
no prose paragraphs. Function/class-level docstrings only, no inline
comments, single-word naming where reasonable — all existing
conventions, unchanged.

REQUIREMENTS

- Upload endpoint accepts all 8 format categories listed above, rejects
  anything outside that list with the existing ApiError pattern.
- Extraction + chunking fully replaced with Docling/HybridChunker per
  the config above.
- Chunk/ResponseChunk schemas extended with page/heading/section.
- Edge cases per the rag skill: a file shorter than one chunk still
  works via Docling's native handling; a page/image yielding zero
  extractable text even after OCR logs a warning rather than silently
  dropping or crashing.
- Dockerfile pre-warms the new model caches; tiktoken pre-warm removed.
- Existing test suite updated, not just preserved:
  - The current ".txt upload returns 400" test is now WRONG since .txt
    is accepted — replace it with a genuinely unsupported extension
    (e.g. .zip or similar) for the rejection test.
  - Add test fixtures and cases for at least: .docx, .xlsx, .pptx,
    .html, .csv, and one image file, each producing a successful
    chunked response.
  - Update assertions that previously checked for the old Chunk shape
    or raw (non-contextualized) text to match the new behavior.
  - Re-verify the "image-only page" test's expected outcome — with OCR
    now enabled, this may legitimately succeed in extracting text
    rather than producing the old warning-only outcome. Test for
    whichever is actually true of the implementation, don't assume the
    old expectation still holds.

ACCEPTANCE CRITERIA

- Uploading one real file of each of the 8 accepted format categories
  returns 200 with a populated, correctly chunked response including
  page/heading/section where applicable.
- Uploading a genuinely unsupported format (not .txt — pick something
  actually excluded) returns 400.
- A PDF with at least one scanned/image-only page either produces
  usable OCR'd text in its chunks, or logs a clear warning if OCR
  genuinely found nothing — verify which, don't assume.
- `docker compose up --build` still works end to end from server/;
  expect a longer build time and larger image, not a failure.
- Full test suite passes, including the corrected rejection test and
  new format fixtures.
- No new commits exist; branch unchanged at end of session.

EXPLAIN-BACK REQUIREMENT

Append to PHASE_01_PLAN_01_SUMMARY.md, as short bullet points only:
exact Docling/pipeline configuration used (confirm it matches standard
pipeline + RapidOCR, no VLM), how the rejection test was fixed, what
happened with the image-only-page test (OCR succeeded vs. warning
logged — state which), and the actual observed build time/image size
impact.

```

```
