# ======================================================
# ====================[ DOCKERFILE ]====================
# ======================================================

FROM python:3.12-slim

# ======================================================
# ===================[ ENVIRONMENT ]====================
# ======================================================

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HF_HOME=/opt/huggingface

# ======================================================
# =====================[ INSTALL ]======================
# ======================================================

WORKDIR /server

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 libxcb1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    torch==2.14.1+cpu \
    torchvision==0.29.1+cpu

RUN pip install --no-cache-dir -r requirements.txt

# ======================================================
# ======================[ CACHE ]=======================
# ======================================================

RUN docling-tools models download layout tableformer rapidocr \
    --rapidocr-backend-lang onnxruntime:ch

COPY app/schemas/constants.py /tmp/atlas_constants.py

RUN python -c "import sys; sys.path.insert(0, '/tmp'); from atlas_constants import EmbeddingConstants; from transformers import AutoTokenizer; from FlagEmbedding import BGEM3FlagModel; config = EmbeddingConstants(); AutoTokenizer.from_pretrained(config.EMBEDDING_MODEL); BGEM3FlagModel(config.EMBEDDING_MODEL, use_fp16=config.EMBEDDING_USE_FP16)"

ENV DOCLING_ARTIFACTS_PATH=/root/.cache/docling/models
ENV HF_HUB_OFFLINE=1

# ======================================================
# ======================[ SERVE ]=======================
# ======================================================

COPY app ./app
COPY alembic.ini .
COPY migrations ./migrations

ARG PORT

ENV PORT=$PORT

EXPOSE ${PORT}

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"$PORT\""]
