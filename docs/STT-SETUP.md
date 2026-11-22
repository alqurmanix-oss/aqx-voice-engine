# Offline STT setup (faster-whisper)

The local adapter is implemented, but inference remains disabled by default.

## Provision a local model

Enable the optional runtime in the container build by setting this in `.env`:

```dotenv
AQX_EXTRAS=stt-whisper
```

Then rebuild with `docker compose up --build`. For local development, install with `pip install -e '.[stt-whisper]'`.

Provision a pinned checkpoint on an operator-controlled machine. The selected upstream checkpoint is `Systran/faster-whisper-large-v3` (CTranslate2 format, MIT license, 100 languages declared by its model card). Review the model card and license at https://huggingface.co/Systran/faster-whisper-large-v3, then provision an immutable commit SHA:

```bash
pip install huggingface_hub
python scripts/provision_whisper.py --revision <immutable-commit-sha> --destination /models/whisper-large-v3
```

Copy the resulting directory into the server's persistent model volume at `/models/whisper-large-v3/`.

The directory must contain the CTranslate2 model files and tokenizer assets expected by faster-whisper. Do not set `STT_MODEL_PATH` to a hosted model ID: the adapter accepts a local directory only and does not download weights during requests.

Verify model license, source revision, language coverage and hardware requirements before deployment. Weights are not stored in Git.

## Enable

Set these values in `.env`:

```dotenv
STT_ADAPTER=faster-whisper
STT_MODEL_PATH=/models/whisper-large-v3
STT_DEVICE=cpu
STT_COMPUTE_TYPE=int8
```

For NVIDIA GPU deployment, select a compatible CUDA/CTranslate2 stack and configure the device and compute type accordingly. The included Compose profile is CPU-oriented.

## Request

Send multipart form data to `POST /v1/stt` with header `X-AQX-API-Key` and field `file`. Optional `language` accepts a language code; omit it for automatic language detection.

The response includes text, detected language and language probability. Uploaded audio is written to a temporary file and deleted after processing.

## Readiness

A present model directory and installed runtime are necessary but not sufficient. Run representative audio tests for each target language/dialect, record WER/CER and latency in `LANGUAGE-VALIDATION.md`, and only then mark that language verified. No language is verified by this scaffold.
