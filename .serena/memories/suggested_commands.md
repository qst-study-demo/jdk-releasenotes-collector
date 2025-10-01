# よく使うコマンド
- `python run/extract_jdk.py` : OpenJDK リリースノートから Issue リストを抽出。
- `python run/fetch_jdk_issues.py` : 抽出した Issue の XML を JBS から取得 (時間が掛かる)。
- `python run/filter_jdk_issues.py --source DIR --output DIR` : 取得済み XML を分類し、調査対象/除外を振り分け。
- `python run/aggregate_jdk_issues.py` : 分類結果をもとに詳細・リリース別・領域別 CSV を生成。
- `python run/merge_jdk_issues.py --content-mode summary` : Issue のタイトル・要約を単一ファイルへ統合 (NotebookLM 用)。