# ======================================================
# ====================[ DOCKERFILE ]====================
# ======================================================

FROM python:3.12-slim

# ======================================================
# ===================[ ENVIRONMENT ]====================
# ======================================================

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TIKTOKEN_CACHE_DIR=/opt/tiktoken_cache

# ======================================================
# ======================[ BUILD ]=======================
# ======================================================

WORKDIR /server

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /opt/tiktoken_cache \
    && python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"

COPY app ./app

# ======================================================
# ======================[ SERVE ]=======================
# ======================================================

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]