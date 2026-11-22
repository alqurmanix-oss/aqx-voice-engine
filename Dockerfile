FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libgomp1 && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY aqx_voice ./aqx_voice
ARG AQX_EXTRAS=""
RUN if [ -n "$AQX_EXTRAS" ]; then pip install ".[${AQX_EXTRAS}]"; else pip install .; fi
EXPOSE 8080
CMD ["uvicorn", "aqx_voice.main:app", "--host", "0.0.0.0", "--port", "8080"]
