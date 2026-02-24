import argparse
import sys
from pathlib import Path

from .locker import lock_file, unlock_file
from .config import load_password


def main():
    parser = argparse.ArgumentParser(description="Lock/unlock a file with encryption")
    parser.add_argument("target", help="Path to the target file to lock or unlock")
    parser.add_argument(
        "-c", "--config", default="config.json", help="Path to config file"
    )
    parser.add_argument(
        "-u", "--unlock", action="store_true", help="Decrypt mode (unlock)"
    )
    args = parser.parse_args()

    password = load_password(args.config)

    try:
        if args.unlock:
            result = unlock_file(args.target, password)
            print(f"Success! Decrypted: {result['decrypted_path']}")
            print(f"Original name: {result['original_name']}")
        else:
            result = lock_file(args.target, password)
            print(f"Success! Output: {result['tar_path']}")
            print(f"Original name: {result['original_name']}")
            print(f"Encrypted name: {result['encrypted_name']}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
