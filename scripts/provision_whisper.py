#!/usr/bin/env python3
"""Download a pinned CTranslate2 Whisper checkpoint for offline serving."""
import argparse
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", required=True, help="Immutable Hugging Face commit SHA")
    parser.add_argument("--destination", default="/models/whisper-large-v3")
    args = parser.parse_args()
    if len(args.revision) < 7 or not all(c in "0123456789abcdef" for c in args.revision.lower()):
        parser.error("--revision must be a hexadecimal commit SHA, not a branch name")
    from huggingface_hub import snapshot_download
    path = snapshot_download(
        repo_id="Systran/faster-whisper-large-v3",
        revision=args.revision,
        local_dir=Path(args.destination),
    )
    print(f"Provisioned Systran/faster-whisper-large-v3 at {args.revision}")
    print(f"Local model directory: {path}")
    print("Record this revision and the model license in the deployment inventory.")

if __name__ == "__main__":
    main()
