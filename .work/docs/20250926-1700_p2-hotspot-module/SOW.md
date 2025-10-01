# Statement of Work

## 依頼概要
- `step4.資料作成/作業フォルダ/Issue一覧/issue_jdk-21.0.6+7.txt` に、`list_underscored.txt` で管理されるカテゴリ情報のうち `P2_Backport_hotspot` を反映させたい。
- `step4.資料作成/作業フォルダ/list_underscored.txt` を長期的に扱いやすくするための Python モジュールを新設したい。

## 事前調査メモ
- `issue_jdk-21.0.6+7.txt` の各レコードは `-----` 区切りで Title/Description を保持しており、カテゴリ情報は未付与状態。
- `list_underscored.txt` の対象行は `P2_Backport_hotspot_JDK-<id>_<概要>` 形式。`JDK-8340156` など複数が該当。
- 既存の `run/update_list_underscored.py` に `read_list_lines` 等の再利用可能なユーティリティが存在。

## 影響範囲 (LSP 抽出済みシンボル)
- `run/update_list_underscored.py:read_list_lines`
- `run/update_list_underscored.py:ISSUE_ID_PATTERN`
- `run/update_list_underscored.py:UpdateSummary` (再利用検討のため確認済み。実際の import は `read_list_lines` と正規表現定数に限定予定)
- 新規モジュール (仮称 `run/list_long_term.py`) — 新規作成
- `step4.資料作成/作業フォルダ/Issue一覧/issue_jdk-21.0.6+7.txt` — 文書更新

## 対応方針
1. `list_underscored.txt` を読み出し、`P2_Backport_hotspot` 行から Issue ID 一覧を取得。
2. `issue_jdk-21.0.6+7.txt` の各レコードを走査し、対象 Issue に `Category: P2_Backport_hotspot` 行を Title と Description の間に挿入。
3. `run/list_long_term.py` (仮) を作成し、`list_underscored.txt` を読み込み以下機能を提供:
   - レコードを `priority`, `workstream`(Backport/Bug 等), `subsystem`(hotspot 等), `issue_id`, `summary` に分解する `ListRecord` データクラス。
   - `load_records(path: Path) -> Sequence[ListRecord]` での一括読み込み。
   - `filter_by_category(records, priority, subsystem)` 等のフィルタ関数。
   - `main` で `--category P2_Backport_hotspot` のような抽出 CLI (標準出力へ Issue ID 一覧出力) を用意し、長期運用に向けた再利用性を確保。
4. 既存スクリプトへ副作用が及ばないことを確認 (新規モジュールは import されない構成)。

## Atomic Tasks
- AT1: `list_underscored.txt` から `P2_Backport_hotspot` 対象の Issue ID リストを抽出するロジックを設計 (テキスト整合性確認のみ)。
- AT2: `issue_jdk-21.0.6+7.txt` にカテゴリ行を挿入 (対象 Issue のみに限定)。
- AT3: `run/list_long_term.py` を実装し、CLI で `P2_Backport_hotspot` を抽出できることを確認。
- AT4: 簡易実行テスト (`python run/list_long_term.py --list-path ... --category P2_Backport_hotspot`) でフィルタ結果を検証。

## 検証方針
- 更新後の `issue_jdk-21.0.6+7.txt` で、`P2_Backport_hotspot` 対象レコードにのみ `Category: ...` 行が追加されていることを目視確認。
- 新規モジュールの CLI を dry-run 実行し、対象 Issue ID が抽出できることを確認。
- `git diff` で不要な差分が混入していないかチェック。

## リスク・懸念
- `issue_jdk-21.0.6+7.txt` のフォーマットを乱さないよう、追加行の位置と改行制御に注意。
- `list_underscored.txt` の書式が将来的に変わった場合、パーサの保守が必要になる。可能な範囲でロバストな正規化処理を組み込む。

ご確認のうえ、作業着手可否をご指示ください。

## 追加スコープ (2025-09-26 2nd request)
- `run/list_long_term.py` に Issue 一覧へカテゴリを一括付与する機能を追加し、`P2_Backport_hotspot` 該当 Issue 全てへカテゴリ行を挿入できるようにする。
- `step4.資料作成/作業フォルダ/Issue一覧/` 配下の全 Issue ファイルに対し、該当 Issue ID を検出してタイトル直後に `Category: <カテゴリ名>` を追記する。
- 既存のカテゴリ行が別値で存在する場合は正準カテゴリに置き換える。
- 乾式実行 (dry-run) で差分確認できる CLI オプションを用意する。
- 変更適用後、全 Issue ファイルに所定カテゴリが追加されたことを検証する。
## 追加スコープ (2025-09-26 3rd request)
- `list_underscored.txt` に記載された全カテゴリを対象に Issue ファイルへ `Category: <正準名>` を付与する。
- 既に `Category:` 行が存在する場合は正準カテゴリへ置換し、それ以外は Title 直下に挿入する。
- `run/list_long_term.py` のカテゴリ適用処理は全カテゴリを扱えるよう汎用化する。
- 全 Issue ファイルでカテゴリが欠落していないことを確認するため、適用後に差分と件数サマリを検証する。
## 追加スコープ (2025-09-26 4th request)
- Issue ファイルでは `Category:` 行を廃止し、代わりに `Priority:`, `Type:`, `Component:` 行を必ず挿入する。
- `run/list_long_term.py` の適用処理を上記 3 行の整形・置換に対応させる。
- 既存 Issue のメタ情報を一括で再適用し、全レコードで 3 行が揃っていることを確認する。
