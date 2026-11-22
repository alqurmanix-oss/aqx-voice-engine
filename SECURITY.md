# Security policy

Do not expose the API publicly with the example key. Set a unique high-entropy `AQX_API_KEY`, terminate TLS at a trusted reverse proxy, restrict network access, and rotate credentials if exposed.

Report vulnerabilities privately to the repository owner. Do not publish secrets, recordings, access tokens, or model weights in issues or commits.

The initial scaffold is not a production security certification. Before production, add persistent rate limiting, structured audit logging, retention/deletion controls, dependency scanning, and deployment-specific hardening.
