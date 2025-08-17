"""One-shot helper to create demo groups in Open WebUI."""

from __future__ import annotations

import argparse
import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--group", action="append", required=True)
    args = parser.parse_args()

    client = httpx.Client(headers={"Authorization": f"Bearer {args.api_key}"})
    for group in args.group:
        resp = client.post(f"{args.base_url}/api/v1/groups", json={"name": group})
        if resp.status_code >= 400:
            print(f"Failed to create group {group}: {resp.text}")


if __name__ == "__main__":
    main()
