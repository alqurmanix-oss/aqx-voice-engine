# AQX Voice Engine

Self-hosted, privacy-first speech platform for AQX. Runtime inference is designed to execute locally without OpenAI, Azure, ElevenLabs, or other hosted inference APIs.

> **Status: integration scaffold.** Local STT and TTS adapters are implemented, but actual inference is disabled by default until model weights and compatible runtimes are provisioned and tested. No language or model is considered production-ready until local end-to-end tests pass.

## Scope
- Local speech-to-text (STT) with faster-whisper and automatic language detection.
- Local multilingual text-to-speech (TTS) adapter using Chatterbox Multilingual V3.
- Registry metadata for languages, dialects, licenses, hardware and validation.
- Local model weights; weights are never committed to Git.
- API-key authentication, bounded uploads, health and capability reporting.

## Quick start
```bash
cp .env.example .env
# Set AQX_API_KEY to a long random value
# Set AQX_EXTRAS=stt-whisper,tts-chatterbox to include both optional runtimes in the image
docker compose up --build
```

API: `http://localhost:8080`. `/health` reports process health only. Enable STT/TTS only after following `docs/STT-SETUP.md` and `docs/TTS-SETUP.md`. Without local weights and optional runtimes, speech endpoints deliberately return HTTP 503; there is no remote fallback.

## Models and language coverage
- STT: see `docs/STT-SETUP.md` and `models/registry.json`.
- TTS: see `docs/TTS-SETUP.md` and the upstream [Chatterbox model card](https://huggingface.co/ResembleAI/chatterbox).

Upstream language declarations are not AQX test results. See `docs/LANGUAGE-VALIDATION.md`; only specifically installed and tested language/dialect combinations may be advertised as verified.

## Privacy
The application contains no hosted inference-provider client. Model provisioning is an operator action. Runtime Hugging Face access is disabled in the container and TTS adapter. For strict offline operation, provision and checksum dependencies and weights, then block outbound network traffic at the host/container boundary.

Supabase integration is intentionally out of scope for this independent repository.
