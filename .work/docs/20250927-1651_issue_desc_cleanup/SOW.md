# Statement of Work: issue_jdk-21.0.6+7.txt の Description 空行削除モジュール作成

## 要件
- 対象ファイル: `1.INPUT作成/2.情報抽出/1.Issueの内容整理/Issue一覧/issue_jdk-21.0.6+7.txt`
- `Description:` 行とその直後の `(no description)` 行の組み合わせを削除する Python モジュールを新規作成する
- 正準入力のみを扱う (想定外書式はエラーとし黙って補正しない)
- 既存資料への副作用を最小限に保ちつつ、再利用しやすい形で提供する

## 進め方 (AT 単位)
1. AT1: 対象ファイル構造と既存 Python ユーティリティの把握
2. AT2: モジュール設計 (CLI I/F・処理フロー・入出力仕様の明文化)
3. AT3: 実装 (入出力検証・例外処理含む)
4. AT4: 動作確認 (対象ファイルに対してのドライランを実施し、削除結果を確認)

## 影響範囲の事前調査 (Serena LSP)
- `bk/run/filter_jdk_issues.py`: 主要シンボル `IssueData`, `RuleMatch`, `IssueClassification`, `normalize_text`, `parse_issue`, `IssueRepository`, `IssueClassifier`, `build_arg_parser`, `main`
- 調査結果より、既存シンボルには手を加えず新規モジュール追加のみで要件を満たせる見込み

## スコープ
- 新規モジュール (例: `bk/run/remove_empty_descriptions.py`) の作成
- 対象ファイルの加工ロジック提供

## 非スコープ
- 他 Issue ファイルや既存モジュールの改修
- パイプラインや CI 設定の更新

## 検証
- 単体: テストデータ (対象ファイルのコピー) を用いた CLI 実行結果確認
- 本番適用は利用者が自己責任で実施

## リスクと対応
- 想定外フォーマット -> 行解析時に検証し、検証失敗時は明示的に例外を投げる
- 誤削除 -> 事前にバックアップファイルへ書き出すオプションを提供

以上の方針で進めて問題なければご承認ください。
