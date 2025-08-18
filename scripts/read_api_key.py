#!/usr/bin/env python3
"""Script to read OpenWebUI API key from file."""

import os
import sys

def read_api_key(file_path: str = ".owui_api_key") -> str:
    """Read API key from file."""
    try:
        with open(file_path, "r") as f:
            api_key = f.read().strip()
            if api_key:
                return api_key
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error reading API key: {e}", file=sys.stderr)
    
    return ""

def main():
    """Main function."""
    api_key = read_api_key()
    if api_key:
        print(api_key)
        return 0
    else:
        print("No API key found", file=sys.stderr)
        return 1

if __name__ == "__main__":
    exit(main())
