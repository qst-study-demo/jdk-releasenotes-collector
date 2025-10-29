# HTMLテンプレートジェネレーター

## 概要

このディレクトリには、JDK Issue AnalyzerのHTMLレポート生成用テンプレートが含まれています。

テンプレート方式を採用することで、以下のメリットがあります：

1. **高速な生成**: テンプレートの読み込みは1回のみ、データの注入のみを行うため高速
2. **保守性の向上**: HTMLとロジックの分離により、デザインの変更が容易
3. **カスタマイズ性**: テンプレートを編集するだけでデザインを変更可能

## パフォーマンス

ベンチマーク結果（373件のIssue）：

```
データ読み込み時間:    0.002秒
HTML生成時間（平均）:  0.003秒
処理速度:            130,091 Issues/秒
```

## ファイル構成

```
templates/
├── README.md                  # このファイル
└── report_template.html       # HTMLレポートのテンプレート
```

## テンプレート変数

`report_template.html` で使用される変数：

### 基本情報
- `title`: レポートのタイトル
- `summary`: レポートの概要
- `versions_text`: 分析対象バージョン（カンマ区切り）

### 統計情報
- `total_issues`: 総Issue数
- `high_priority_count`: 高優先度Issue数（P1-P2）
- `windows_count`: Windows関連Issue数
- `security_count`: セキュリティ関連Issue数

### データ（JSON形式）
- `issues_data`: Issue一覧のJSONデータ
- `priority_stats`: 優先度別統計のJSONデータ
- `component_stats`: コンポーネント別統計のJSONデータ
- `type_stats`: タイプ別統計のJSONデータ
- `os_stats`: OS別統計のJSONデータ

### HTMLオプション
- `type_options`: タイプフィルタのHTML option要素
- `component_options`: コンポーネントフィルタのHTML option要素

## 使用方法

### 基本的な使い方

```python
from html_generator import HTMLGenerator, prepare_report_data
from jdk_issue_statistics import load_multiple_files

# データの読み込み
stats = load_multiple_files(['jdk_21.0.6.txt', 'jdk_21.0.7.txt'])

# HTMLジェネレーターの初期化
generator = HTMLGenerator()

# レポートデータの準備
data = prepare_report_data(stats, ['21.0.6', '21.0.7'])

# HTMLレポートの生成
generator.generate(data, 'output.html')
```

### カスタム設定を使用

```python
custom_config = {
    'title': 'カスタムタイトル',
    'summary': 'カスタム概要'
}

data = prepare_report_data(stats, versions, custom_config)
generator.generate(data, 'custom_report.html')
```

### generate_report.pyから使用

```bash
cd scripts
python3 generate_report.py 21.0.6 21.0.7 21.0.8
```

## テンプレートのカスタマイズ

`report_template.html` を直接編集してデザインをカスタマイズできます。

### CSSスタイルの変更

```html
<style>
    /* カラースキームの変更 */
    header {
        background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
    }
</style>
```

### 新しいセクションの追加

```html
<div class="custom-section">
    <h2>{{ custom_title }}</h2>
    <p>{{ custom_content }}</p>
</div>
```

対応するデータを `prepare_report_data()` で追加：

```python
data['custom_title'] = 'カスタムタイトル'
data['custom_content'] = 'カスタムコンテンツ'
```

## テンプレートエンジン

### Jinja2（推奨）

Jinja2がインストールされている場合、自動的に使用されます。

```bash
pip install jinja2
```

### フォールバック（単純置換）

Jinja2が利用できない場合、シンプルな文字列置換が使用されます。

## トラブルシューティング

### テンプレートが見つからない

```
FileNotFoundError: [Errno 2] No such file or directory: '.../templates/report_template.html'
```

→ `HTMLGenerator` の初期化時にテンプレートディレクトリを指定：

```python
generator = HTMLGenerator(template_dir='/path/to/templates')
```

### 変数が置換されない

Jinja2を使用している場合は `{{ variable }}` の形式、
フォールバック使用時も同じ形式で動作します。

## 今後の拡張

- 複数のテンプレート対応（ダークモード、コンパクトモードなど）
- カスタムチャートタイプの追加
- PDFエクスポート機能
- インタラクティブな比較ビュー

## ライセンス

このテンプレートは、JDK Issue Analyzerの一部として提供されています。
