# SOW: step4 list.txt アンダーバー整形 + description 付与モジュール

## 目的
- `step4.資料作成/list.txt` の内容を、`P` 系行をレコード境界と見なしつつ各行をアンダーバーで連結し、対応する `jdk_issues_combined.txt` から取得した Description を末尾に付与する Python モジュールを実装する。

## スコープ
- 入力: 既存ファイル `step4.資料作成/list.txt` および `step4.資料作成/jdk_issues_combined.txt`
- 出力: アンダーバー区切り + Description を付与したテキストを同ディレクトリに新規ファイルとして書き出す（デフォルト `list_underscored.txt`）
- 実装: `step4.資料作成/hyphenate_list.py` に処理関数と CLI を実装
- テスト: モジュールを実行し、Description が正しく連結されることを確認

## LSP 調査結果（影響シンボル）
- `run/aggregate_jdk_issues.py`: `serena__get_symbols_overview` でシンボル構造を確認済み。今回の処理とは独立、変更不要。
- 既存の list 整形処理は今回モジュール内で完結するため、影響範囲は `hyphenate_list.py` および新規出力ファイルに限定。

## アウトオブスコープ
- `list.txt` / `jdk_issues_combined.txt` の内容変更
- 他ディレクトリ (`run/`, `step1~3`) のスクリプト修正
- CLI 引数・環境変数の追加要件（既定引数以外）

## タスク分割 (AT)
1. AT1: `list.txt` と `jdk_issues_combined.txt` の構造を確認し、Description の取得ロジックを設計
2. AT2: `hyphenate_list.py` にアンダーバー連結 + Description 付与処理を実装し、CLI 引数を整備
3. AT3: 実装関数を実行して出力内容を検証、結果を報告
