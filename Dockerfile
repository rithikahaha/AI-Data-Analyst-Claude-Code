FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencies first so this layer is cached until requirements.txt changes.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Bake the sample warehouse and churn model into the image, so a container
# starts serving immediately instead of rebuilding data on first request.
RUN python -m scripts.export_raw_sources \
    && python -m pipelines.etl \
    && python -m ml.train_churn_model

# Run as a non-root user: a compromised dashboard shouldn't own the container.
RUN useradd --create-home --uid 10001 app \
    && mkdir -p /app/logs \
    && chown -R app:app /app
USER app

EXPOSE 8501

# Streamlit exposes its own liveness endpoint. Python is used for the probe
# because the slim image has no curl.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health', timeout=4).status == 200 else 1)"

CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
