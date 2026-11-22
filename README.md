# AQX Voice Engine

Self-hosted, privacy-first speech platform for AQX. Runtime inference is designed to execute locally without OpenAI, Azure, ElevenLabs, or other hosted inference APIs.

> **Status: foundation scaffold.** API structure and deployment files are being established. No language or model is considered production-ready until local end-to-end tests pass.

## Scope
- Local text-to-speech (TTS) and speech-to-text (STT) adapters.
- Language detection where supported by the selected STT model.
- Registry metadata for languages, dialects, licenses, hardware and validation.
- Local model weights; weights are never committed to Git.
- Authenticated API, bounded uploads, health and capability reporting.

## Quick start

```bash
cp .env.example .env
# Set AQX_API_KEY to a long random value
docker compose up --build
```

API: `http://localhost:8080`. `/health` reports process health only. TTS/STT deliberately return 503 until a compatible local inference adapter is installed and validated; there is no remote fallback.

## Model coverage
See `models/registry.json` and `docs/LANGUAGE-VALIDATION.md`. Registry candidates are not verified support. Review the exact upstream model card, license, language/dialect coverage, hardware needs and quality before enabling a model. Do not claim support for every world language without reproducible tests.

## Privacy
The application has no hosted inference-provider client. Operators may need outbound access to provision packages and model weights; after provisioning, enforce offline runtime networking if required. Supabase integration is intentionally out of scope for this independent repository.
