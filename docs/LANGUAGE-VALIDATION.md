# Language validation ledger

No language is verified by this initial integration.

For every model + language + locale/dialect combination, record:

| Field | Required evidence |
|---|---|
| Model/version | Exact upstream ID and immutable revision |
| License | License text and commercial-use review |
| Language/locale | ISO language tag; dialect where applicable |
| STT quality | Representative test set, sample count, WER/CER |
| TTS quality | Native-speaker intelligibility/naturalness review and sample set |
| Hardware | CPU/GPU, VRAM/RAM, latency and real-time factor |
| Privacy | Confirm no runtime inference egress |
| Result | Pass/fail, date, reviewer, reproducible test command |

The Chatterbox multilingual model card lists Arabic and 22 other named languages. That is upstream-declared coverage, not AQX validation. Egyptian Arabic dialect quality is not established by the general Arabic language listing.

Do not claim “all world languages”. Coverage is the union of specifically documented, licensed, installed, and tested models. A language being listed upstream is not equivalent to acceptable AQX quality.
