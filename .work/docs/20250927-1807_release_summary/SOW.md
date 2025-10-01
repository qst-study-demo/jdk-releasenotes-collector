# Statement of Work: JDKリリースノート整形

## 背景
- `run/jdk_OpenJDK 21.0.6 Released.txt` に列挙された JDK 課題 ID から、`run/jdk_issues/` 以下に保存済みの XML を参照し、指定フォーマットでテキスト出力する仕組みが求められている。
- 出力ファイル名は入力ファイル名に `_output.txt` を固定付与する必要があり、非正準表現やフォールバックは不可。

## 対応方針
- 新規スクリプト（仮称: `generate_release_notes.py`）を `run/` 直下に追加し、CLI 引数で入力ファイルを受け付ける。
- 課題 ID の正準性チェックと重複排除は既存ロジックを再利用するため、`run/fetch_jdk_issues.py` の `load_issue_ids` をインポートして利用する。
- 各 JDK 課題の XML は `xml.etree.ElementTree` で解析し、Title / Priority / Type / Component / Description / OS を抽出。Description と OS は要素が存在する場合のみ出力。
- `jdk_issues` ディレクトリが存在しない場合は即座に例外送出し処理を停止。

### 対象シンボル (LSP 抽出)
- `run/fetch_jdk_issues.py:load_issue_ids`
- `run/fetch_jdk_issues.py:JDK_ID_PATTERN`

## 成果物
- `run/jdk_OpenJDK 21.0.6 Released.txt_output.txt`
- 発行用スクリプト `run/generate_release_notes.py`

## タスク (Atomic)
1. `generate_release_notes.py` の骨格を実装し、引数解析と `jdk_issues` 存在チェックを追加。
2. `load_issue_ids` を用いて入力ファイルから課題 ID を取得する処理を組み込む。
3. 課題 XML から必要フィールドを抽出し、指定フォーマットで文字列生成するロジックを作成。
4. 生成結果を `<入力ファイル名>_output.txt` に書き出し、ファイル内容を確認。

## 検証
- 入力ファイル: `run/jdk_OpenJDK 21.0.6 Released.txt`
- コマンド例: `python run/generate_release_notes.py run/jdk_OpenJDK\ 21.0.6\ Released.txt`
- 出力内容を目視で確認し、必要フィールドが欠落 / 冗長に出力されていないことを検証。
