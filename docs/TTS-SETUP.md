# Offline multilingual TTS setup

The repository includes an adapter for Chatterbox Multilingual V3. The upstream model card identifies Arabic among its 23 supported languages and states an MIT license. Treat this as upstream-declared coverage, not a claim that AQX has verified every language or dialect.

## 1. Review and pin the model

Review the current model card and license:
- https://huggingface.co/ResembleAI/chatterbox
- https://github.com/resemble-ai/chatterbox

Choose an immutable commit SHA from the model repository. Do not provision from a moving branch for production.

## 2. Provision weights

Enable the optional runtime in the container build by setting this in `.env`:

```dotenv
AQX_EXTRAS=tts-chatterbox
```

Then rebuild with `docker compose up --build`. For local development, install `pip install -e '.[tts-chatterbox]'` plus a platform-compatible PyTorch/torchaudio build. If both speech tasks are required, set `AQX_EXTRAS=stt-whisper,tts-chatterbox`.

Set `HF_HOME` to the persistent model volume, then provision the pinned revision:

```bash
export HF_HOME=/models/huggingface
python scripts/provision_chatterbox.py --revision <immutable-commit-sha>
```

Copy the resulting Hugging Face cache to the inference host's `/models/huggingface` volume. The serving process forces Hugging Face offline mode before importing Chatterbox; it must not fetch model files during a user request.

## 3. Enable TTS

Set in `.env`:

```dotenv
TTS_ADAPTER=chatterbox
TTS_DEVICE=cpu
TTS_VOICE_DIR=/models/voices
HF_HOME=/models/huggingface
```

Use a compatible CUDA/PyTorch/torchaudio stack and `TTS_DEVICE=cuda` on a suitable GPU host. The default Compose profile is CPU-oriented and is not a performance guarantee.

## 4. API

Call `POST /v1/tts` with JSON:

```json
{"text":"أهلاً بك في AQX","language":"ar"}
```

Include `X-AQX-API-Key`. The response is a WAV file. Language codes are normalized from tags such as `ar-EG` to the base code `ar`.

Optional voice IDs map to WAV prompt files under `TTS_VOICE_DIR`, e.g. voice ID `female_01` resolves only to `/models/voices/female_01.wav`. Only use recordings with documented speaker consent. Do not accept arbitrary paths from API callers.

## Coverage and quality gates

The upstream multilingual card lists Arabic, Danish, German, Greek, English, Spanish, Finnish, French, Hebrew, Hindi, Italian, Japanese, Korean, Malay, Dutch, Norwegian, Polish, Portuguese, Russian, Swedish, Swahili, Turkish and Chinese. It describes general Arabic; it does not establish Egyptian Arabic dialect quality.

Before marking any locale verified, run native-speaker evaluations for intelligibility, pronunciation, naturalness, numbers/names and dialect fidelity. Record results in `LANGUAGE-VALIDATION.md`. The model's built-in watermarking is retained; do not remove it.
