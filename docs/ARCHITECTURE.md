# Architecture

Request flow: client -> FastAPI -> authentication and validation -> task router -> local model adapter -> local model volume.

- API: FastAPI, API-key authentication, bounded request bodies.
- Model adapters: separate STT/TTS implementations. They must load local weights and must not call hosted inference APIs.
- Registry: model ID/revision, license review, languages, dialects, hardware profile and validation evidence.
- Storage: dedicated model volume; audio retention must be explicitly configured before production.

The included Compose profile is a lightweight CPU-oriented API scaffold. GPU inference requires a compatible NVIDIA host, container runtime and model-specific CUDA stack. No GPU deployment is claimed here.

Supabase integration is intentionally out of scope for this independent repository. It can be added later only as an explicit optional control-plane/storage integration.

For strict offline runtime, provision and checksum dependencies and weights, then block outbound network traffic at the host/container boundary.
