#!/usr/bin/env python3
"""Extract JDK issue identifiers from list.txt and write them to jdk.txt."""
from pathlib import Path
import re


def main() -> None:
    source_path = Path("list.txt")
    if not source_path.is_file():
        raise FileNotFoundError("list.txt was not found in the current directory")

    content = source_path.read_text(encoding="utf-8")
    matches = re.findall(r"JDK-\d+", content)

    seen = set()
    unique_ids = []
    for identifier in matches:
        if identifier not in seen:
            seen.add(identifier)
            unique_ids.append(identifier)

    output_path = Path("jdk.txt")
    output_path.write_text("\n".join(unique_ids), encoding="utf-8")


if __name__ == "__main__":
    main()
