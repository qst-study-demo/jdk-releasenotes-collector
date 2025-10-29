---
name: jdk-issue-analyzer
description: Analyze JDK issues between versions to identify changes that impact application functionality. Use for JDK upgrade impact analysis, filtering bug fixes affecting Windows 11 applications, or generating reports on breaking changes.
---

# JDK Issue Analyzer

JDKバージョン間のIssue(バグ修正、機能追加、変更など)を分析し、アプリケーションへの影響を評価するスキルです。特にWindows 11環境でのJDKバージョンアップ時の影響調査に有用です。

**主な機能:**
- 複数バージョンの同時検索・比較
- Issue統計情報の可視化
- 優先度・タイプ・コンポーネント別のグループ化
- バージョン横断的な統合分析
- キーワード・フィルタ検索
- HTMLレポート生成

## Core Workflow

### 1. バージョン選択

ユーザーとの対話を通じて、分析対象のJDKバージョンを決定します。以下のバージョンが利用可能です:

- OpenJDK 21.0.6
- OpenJDK 21.0.7
- OpenJDK 21.0.8

複数バージョンを選択可能で、選択されたバージョンのすべてのIssueが統合分析されます。

ユーザーが具体的なバージョンを指定していない場合は、以下のような質問で要望を明確化してください:

- 「どのJDKバージョン間での変更を分析しますか?」
- 「現在使用しているJDKバージョンと、アップグレード先のバージョンを教えてください」
- 「すべての利用可能なバージョン(21.0.6, 21.0.7, 21.0.8)を分析しますか?」

### 2. 目的の確認

レポート内容を適切にカスタマイズするため、ユーザーの分析目的を確認します:

- Windows 11環境への影響確認
- セキュリティ関連の変更確認
- パフォーマンス改善の確認
- 特定コンポーネントへの影響確認
- 高優先度Issueの影響評価

### 3. レポート生成

**重要: レポートは必ずHTML形式で生成してください。Word形式やその他の形式は使用しないでください。**

`scripts/generate_report.py`を使用してHTMLレポートを生成します。このスクリプトは内部的に`html_generator.py`のテンプレートジェネレーターを使用しており、高速で保守性の高いHTML生成が可能です。

```bash
cd scripts
python3 generate_report.py 21.0.6 21.0.7 21.0.8
```

**HTMLジェネレーターについて:**
- レポート生成には`html_generator.py`のHTMLGeneratorクラスを使用します
- テンプレート方式により高速（約0.003秒/レポート）で生成されます
- テンプレートは`templates/report_template.html`に格納されています
- Jinja2テンプレートエンジンを使用（フォールバック機能付き）

レポートには以下の情報が含まれます:

- **サマリーダッシュボード**: 総Issue数、高優先度Issue数、Windows関連Issue数、セキュリティ関連Issue数
- **ビジュアルグラフ**: 優先度別、コンポーネント別、タイプ別、OS別の分布（Chart.js使用）
- **インタラクティブなIssue一覧テーブル**: ソート・フィルタリング機能付き

生成されたレポートは`/mnt/user-data/outputs/`にコピーして、ユーザーに提供してください。

### 4. フィードバックと追加分析

レポート生成後、ユーザーに以下のような追加分析を提案します(状況に応じて3つ程度):

1. 「特定のコンポーネント(例: hotspot、security-libs、core-libs)に絞った詳細分析を追加しますか?」
2. 「Windows 11関連のIssueのみの詳細レポートを作成しますか?」
3. 「高優先度(P1-P2)Issueの影響度分析を追加しますか?」
4. 「セキュリティ関連Issueの詳細分析を追加しますか?」
5. 「特定キーワード(例: performance、deprecation、API)での検索分析を追加しますか?」
6. 「バージョン間の比較グラフを追加しますか?」
7. 「複数バージョンのIssueを統合して優先度別にグループ化した分析を追加しますか?」
8. 「各バージョンの統計情報を比較した分析を追加しますか?」

ユーザーが追加分析を希望する場合は、`search_issues.py`の新機能を活用します:

**統計情報を使った分析:**
```bash
# 条件に合致するIssueの統計サマリー
python3 search_issues.py --os windows --stats
python3 search_issues.py --priority P2 --stats --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt
```

**グループ化を使った詳細分析:**
```bash
# Windows関連Issueをコンポーネント別にグループ化
python3 search_issues.py --search "Windows" --group-by component --verbose

# 高優先度Issueをタイプ別にグループ化
python3 search_issues.py --priority P2 --group-by type --verbose
```

**複数バージョンの統合分析:**
```bash
# 全バージョンを統合してセキュリティIssueを優先度別に分析
python3 search_issues.py --search "security" --merge --group-by priority --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt \
  ../references/jdk_OpenJDK21_0_8_Released.txt
```

## Issue検索機能

`scripts/search_issues.py`を使用して、特定条件のIssueを検索できます。

### Issue ID検索

```bash
cd scripts
python3 search_issues.py --id JDK-8320192
python3 search_issues.py --id 8320192  # プレフィックス省略可
```

### キーワード検索

タイトル、説明、コンポーネントからキーワードを検索:

```bash
python3 search_issues.py --search "Windows 11"
python3 search_issues.py --search "platform" --verbose
```

特定フィールドのみを検索:

```bash
python3 search_issues.py --search "security" --search-fields title component
```

### フィルタ検索

```bash
# Priority=P2かつOS=windows
python3 search_issues.py --priority P2 --os windows

# Priority=P3のBug
python3 search_issues.py --priority P3 --type Bug

# hotspotコンポーネントのP4 Issue
python3 search_issues.py --component hotspot --priority P4

# 詳細表示
python3 search_issues.py --priority P3 --type Bug --verbose
```

### ファイル指定

特定バージョンのみを検索:

```bash
python3 search_issues.py --priority P2 --os windows --file ../references/jdk_OpenJDK21_0_7_Released.txt
```

### 複数ファイルの検索

複数のJDKバージョンのIssueを同時に検索:

```bash
# 複数ファイルを指定（ファイル別に結果表示）
python3 search_issues.py --priority P2 --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt \
  ../references/jdk_OpenJDK21_0_8_Released.txt

# Windows関連のIssueを複数バージョンで検索
python3 search_issues.py --search "Windows" --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt
```

### 統合検索（マージモード）

複数ファイルを統合して1つのデータセットとして扱う:

```bash
# 全バージョンを統合してP2のIssueを検索
python3 search_issues.py --priority P2 --merge --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt \
  ../references/jdk_OpenJDK21_0_8_Released.txt
```

### 統計情報の表示

検索条件に合致するIssueの統計情報を表示:

```bash
# Windows関連Issueの統計
python3 search_issues.py --os windows --stats

# P2 Issueの統計を複数バージョンで表示
python3 search_issues.py --priority P2 --stats --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt
```

統計情報には以下が含まれます:
- 総Issue数
- 優先度別統計
- タイプ別統計
- コンポーネント別統計（上位10件）
- OS別統計

### グループ化表示

検索結果を特定の属性でグループ化:

```bash
# 優先度別にグループ化
python3 search_issues.py --priority P2 --group-by priority --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt

# Windows関連Issueをコンポーネント別にグループ化
python3 search_issues.py --search "Windows" --group-by component

# セキュリティ関連Issueをタイプ別にグループ化（詳細表示付き）
python3 search_issues.py --search "security" --group-by type --verbose
```

グループ化オプション:
- `priority`: 優先度別（P1 → P2 → P3...の順）
- `type`: タイプ別（Bug, Sub-taskなど）
- `component`: コンポーネント別（件数の多い順）

## Use Cases

### Windows 11アプリケーションへの影響調査

```bash
cd scripts
# Windows関連のすべてのIssueを検索
python3 search_issues.py --os windows --verbose

# Windows関連の高優先度Issue
python3 search_issues.py --os windows --priority P2

# 複数バージョンでWindows関連Issueをコンポーネント別に分析
python3 search_issues.py --search "Windows" --merge --group-by component --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt \
  ../references/jdk_OpenJDK21_0_8_Released.txt

# Windows関連Issueの統計情報
python3 search_issues.py --os windows --stats
```

### セキュリティ関連の変更確認

```bash
# security-libsコンポーネントの変更
python3 search_issues.py --component security-libs

# セキュリティキーワードで検索
python3 search_issues.py --search "security" --verbose

# 複数バージョンでセキュリティ関連Issueを優先度別に分析
python3 search_issues.py --search "security" --merge --group-by priority --verbose --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt

# セキュリティ関連Issueの統計情報
python3 search_issues.py --component security-libs --stats
```

### パフォーマンス改善の確認

```bash
# hotspotコンポーネントの変更(JVM関連)
python3 search_issues.py --component hotspot

# パフォーマンスキーワードで検索
python3 search_issues.py --search "performance" --verbose

# 複数バージョンでhotspot関連の統計情報を取得
python3 search_issues.py --component hotspot --stats --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt
```

### バージョン横断的な分析

```bash
# 全バージョンでP2のBugを優先度別にグループ化
python3 search_issues.py --priority P2 --type Bug --merge --group-by priority --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt \
  ../references/jdk_OpenJDK21_0_8_Released.txt

# 特定キーワードの出現傾向を各バージョンで比較
python3 search_issues.py --search "deprecat" --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt \
  ../references/jdk_OpenJDK21_0_8_Released.txt

# 各バージョンの統計を比較
python3 search_issues.py --priority P2 --stats --file \
  ../references/jdk_OpenJDK21_0_6_Released.txt \
  ../references/jdk_OpenJDK21_0_7_Released.txt \
  ../references/jdk_OpenJDK21_0_8_Released.txt
```

## プログラマティックな使用

Pythonから直接統計情報を取得することも可能:

```python
from jdk_issue_statistics import load_and_analyze, load_multiple_files

# 単一ファイルを読み込み
stats = load_and_analyze('../references/jdk_OpenJDK21_0_6_Released.txt')

# 複数ファイルを統合
stats = load_multiple_files([
    '../references/jdk_OpenJDK21_0_6_Released.txt',
    '../references/jdk_OpenJDK21_0_7_Released.txt'
])

# 統計情報を取得
print(f"総Issue数: {len(stats.issues)}")
print(f"優先度別: {stats.get_priority_stats()}")
print(f"コンポーネント別: {stats.get_component_stats()}")

# フィルタリング
p3_bugs = stats.filter_issues(priority='P3', type='Bug')
windows_issues = stats.filter_issues(os='windows')
```

## 重要な注意事項

### レポート形式について
- **レポートは必ずHTML形式で生成してください** - Word形式、PDF形式、その他の形式は使用しないでください
- **HTMLレポート生成には必ず`html_generator.py`のテンプレートジェネレーターを使用してください** - 手動でHTMLを構築しないでください
- `generate_report.py`が内部的にHTMLGeneratorクラスを使用するため、このスクリプトを経由してレポートを生成してください

### 一般的な注意事項
- レポート生成前に、必ずユーザーの分析目的を確認してください
- 生成したレポートは必ず`/mnt/user-data/outputs/`にコピーしてください
- 追加分析の提案は、生成したレポートの内容とユーザーの目的に応じて選択してください
- ユーザーが特定のIssueについて詳しく知りたい場合は、`search_issues.py --id`を使用してください
