# SOW: list_underscored.txt への description 追記モジュール作成

## 背景・課題
- `run/list_underscored.txt` には Jira Issue の説明文が未登録であり、`(no description)` のプレースホルダが残っている。
- `run/jdk_issues/{ISSUE_ID}/jdk-{issue_id}.xml` に説明文が含まれているため、これらを用いてリストを更新したい。

## 対象範囲
- 読み取り: `run/list_underscored.txt`, `run/jdk_issues/**/jdk-*.xml`
- 新規作成予定: `run/update_list_underscored.py`（仮称）
- 出力: `run/list_underscored.txt`（上書き更新）

## 非対象
- `step4.資料作成/hyphenate_list.py` など既存のリスト生成ロジックの改修
- XML 以外の情報源からの description 取得
- 付随する CSV 生成や他ファイルの整備

## LSP 調査結果（影響シンボル）
- `step4.資料作成/hyphenate_list.py`: `is_record_marker`, `extract_issue_id`, `load_issue_descriptions`, `hyphenate_records`, `_combine_fields`, `hyphenate_file`, `parse_args`, `main`
  - 既存の list 生成に関わるシンボルを参照範囲に取り込み、処理フォーマットの整合性を確認済み。

## 作業方針（AT 単位）
1. XML 解析ユーティリティ作成
   - `xml.etree.ElementTree` で `<item><description>` を抽出し、HTML エンティティを復元・改行正規化する。
   - 取得した説明を Issue ID (`JDK-\d+`) とマッピング。
2. `list_underscored.txt` の更新処理実装
   - 各行から Issue ID を抽出し、該当する description があれば末尾の `(no description)` を置換。
   - description が無い場合はプレースホルダを維持し、欠落リストをログ出力。
3. CLI 化および入出力バリデーション
   - `--list-path`, `--issues-root`, `--encoding` など最小限の引数を受け取り、Canon 表現で入力を受け付ける。
   - 実行後に更新件数を標準出力へ要約。
4. 動作確認
   - 乾燥ラン（dry-run オプション）で差分を確認し、必要に応じて `run/list_underscored.txt` を更新。

## 成果物
- `run/update_list_underscored.py`
- 更新済み `run/list_underscored.txt`
- 実行手順・確認結果の報告

## 想定リスクと対応
- XML 内 description が HTML エンティティ化されている → `html.unescape` で復元後、改行/空白整理。
- XML に description が無い場合 → `(no description)` を維持し、警告を出力。
- 文字コード問題 → UTF-8 を前提とし、必要に応じて引数で指定可能とする。

## 工数見積
- 実装: 1.5h
- 動作確認: 0.5h
