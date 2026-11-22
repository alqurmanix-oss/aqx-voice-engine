#!/usr/bin/env python3
"""Provision a pinned Chatterbox model revision into the local Hugging Face cache."""
import argparse
import os

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", required=True, help="Immutable Hugging Face commit SHA")
    parser.add_argument("--cache-dir", default=os.environ.get("HF_HOME", "/models/huggingface"))
    args = parser.parse_args()
    if len(args.revision) < 7 or not all(c in "0123456789abcdef" for c in args.revision.lower()):
        parser.error("--revision must be a hexadecimal commit SHA, not a branch name")
    from huggingface_hub import snapshot_download
    path = snapshot_download(
        repo_id="ResembleAI/chatterbox",
        revision=args.revision,
        cache_dir=args.cache_dir,
    )
    print(f"Provisioned ResembleAI/chatterbox at {args.revision}")
    print(f"Snapshot path: {path}")
    print("Keep this revision and the model card/license evidence in your deployment record.")

if __name__ == "__main__":
    main()
