#!/usr/bin/env python3
"""bugs.openjdk.org から JDK 課題 XML を取得して保存するユーティリティ。"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, List
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from xml.etree import ElementTree as ET
import re

BASE_URL_TEMPLATE = "https://bugs.openjdk.org/si/jira.issueviews:issue-xml/{issue}/{issue}.xml"
OUTPUT_ROOT = Path("jdk_issues")
SKIPPED_FILENAME = "skipped.txt"
JDK_ID_PATTERN = re.compile(r"^JDK-\d+$")
REQUEST_TIMEOUT = 30.0  # seconds


class InvalidIssuePayloadError(Exception):
    """期待された形式で課題 XML を取得できなかった場合に送出する例外。"""


def load_issue_ids(source_path: Path) -> List[str]:
    """`jdk.txt` 等から JDK 課題 ID を読み込み、正準表記で返す。"""
    if not source_path.is_file():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {source_path}")

    seen: set[str] = set()
    issue_ids: List[str] = []
    for raw_line in source_path.read_text(encoding="utf-8").splitlines():
        identifier = raw_line.strip()
        if not identifier:
            continue
        if not JDK_ID_PATTERN.fullmatch(identifier):
            raise ValueError(f"正準表記ではない ID を検出しました: {identifier}")
        if identifier in seen:
            continue
        seen.add(identifier)
        issue_ids.append(identifier)
    return issue_ids


def download_issue(issue_id: str) -> bytes:
    """課題 ID に対応する XML をダウンロードして返す。"""
    url = BASE_URL_TEMPLATE.format(issue=issue_id)
    with urlopen(url, timeout=REQUEST_TIMEOUT) as response:  # noqa: S310
        return response.read()


def validate_issue_payload(payload: bytes) -> None:
    """OpenJDK の課題 XML として妥当か検証し、問題があれば例外を送出する。"""
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:  # noqa: B904
        raise InvalidIssuePayloadError(f"XML パースに失敗しました: {exc}")

    if root.tag.lower() != "rss":
        raise InvalidIssuePayloadError(f"予期しないルート要素: {root.tag}")

    channel = root.find("channel")
    if channel is None:
        raise InvalidIssuePayloadError("channel 要素が見つかりません")
    if channel.find("item") is None:
        raise InvalidIssuePayloadError("item 要素が見つからないため課題が存在しません")


def issue_directory(issue_id: str) -> Path:
    """課題 ID ごとの出力ディレクトリを返す。"""
    return OUTPUT_ROOT / issue_id


def build_issue_filename(issue_id: str) -> Path:
    """課題 ID 固有のファイルパスを返す。"""
    numeric_part = issue_id.split("-", 1)[1]
    return issue_directory(issue_id) / f"jdk-{numeric_part}.xml"


def record_skipped(issue_ids: Iterable[str], destination: Path) -> None:
    """スキップした ID をテキストで保存する。"""
    lines = list(issue_ids)
    if lines:
        destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        destination.write_text("", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) > 1:
        print("使用方法: fetch_jdk_issues.py [jdk.txtへのパス]", file=sys.stderr)
        return 2

    source_path = Path(args[0]) if args else Path("jdk.txt")

    try:
        issue_ids = load_issue_ids(source_path)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    skipped: list[str] = []

    for issue_id in issue_ids:
        target_dir = issue_directory(issue_id)
        target_file = build_issue_filename(issue_id)
        if target_file.exists():
            print(f"[SKIP] {issue_id}: 出力ファイルが既に存在するためダウンロードを省略します")
            continue

        try:
            payload = download_issue(issue_id)
            validate_issue_payload(payload)
        except HTTPError as exc:
            skipped.append(f"{issue_id}\tHTTP {exc.code}")
            print(f"[SKIP] {issue_id}: HTTP {exc.code}")
            continue
        except URLError as exc:
            reason = getattr(exc, "reason", exc)
            skipped.append(f"{issue_id}\tURLError {reason}")
            print(f"[SKIP] {issue_id}: URLError {reason}")
            continue
        except InvalidIssuePayloadError as exc:
            skipped.append(f"{issue_id}\tINVALID {exc}")
            print(f"[SKIP] {issue_id}: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001
            skipped.append(f"{issue_id}\tERROR {exc}")
            print(f"[SKIP] {issue_id}: {exc}")
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        target_file.write_bytes(payload)
        print(f"[OK]   {issue_id} -> {target_file}")

    record_skipped(skipped, OUTPUT_ROOT / SKIPPED_FILENAME)
    print(f"完了: 成功 {len(issue_ids) - len(skipped)} 件, スキップ {len(skipped)} 件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
