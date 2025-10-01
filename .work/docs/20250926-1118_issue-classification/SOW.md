# Statement of Work: JDK Issue Canonical Classifier モジュール作成

## 背景・目的
- OpenJDK 21.0.5 → 21.0.8 への更新に伴う非互換リスクを整理するため、`run/jdk_issues/` 配下に取得済みの JBS XML を正規化して分類する仕組みが必要。
- 既存の `filter_jdk_issues.py` と `aggregate_jdk_issues.py` は除外判定と集計までを担うが、調査初期に必要な「リリース・領域・互換性種別・影響範囲・ステータス」軸での分類が未整備。
- Canonical な分類モジュールを新設し、再利用可能な API と CLI を提供する。

## スコープ
1. `run` 配下に JDK Issue を分類する Python モジュール（仮称 `canonical_issue_classifier.py`）を新規追加。
2. 既存の `IssueData` （`filter_jdk_issues.py`）を拡張し、分類に必要な status/resolution/priority 等のメタ情報を保持できるようにする。
3. 上記モジュールで以下の正準属性を付与できる API/CLI を実装。
   - 対象リリース (`21.0.6` / `21.0.7` / `21.0.8` / `21.0.x` / `unknown`)
   - 機能領域カテゴリ（security/runtime_core/gc/compiler_tools/classlib/interop/test_infra/other 等）
   - 互換性種別（security/performance/spec_behavior/behavior_change/bugfix/new_feature/other）
   - 影響範囲（global/platform_specific/component_scoped）
   - 調査ステータスは初期値 `pending_review` を割り当て可能にし、外部入力で更新できる拡張性を残す
   - JBS ステータス（open/in_progress/resolved/closed）
4. CLI で CSV 出力（Issue ID と各正準属性を1行にまとめる）を生成できるようにする。
5. 既存集計 (`aggregate_jdk_issues.py`) と競合しないよう、共通ロジック（リリース判定・領域推定）を再利用できる設計を整備。

## アウトオブスコープ
- JBS からの新規フェッチ、NotebookLM 連携、PPTX 出力ロジックの改修。
- 既存の除外ルール (`IssueClassifier`) の調整。
- CI や追加の自動テスト整備。

## 影響シンボル（LSP調査結果）
- `run/filter_jdk_issues.py:IssueData`
- `run/filter_jdk_issues.py:parse_issue`
- `run/filter_jdk_issues.py:IssueRepository`
- `run/filter_jdk_issues.py:IssueClassifier`
- `run/aggregate_jdk_issues.py:determine_release`
- `run/aggregate_jdk_issues.py:select_feature_area`
- `run/aggregate_jdk_issues.py:detect_highlight_tags`

## 進め方（AT）
1. 既存 XML スキーマを確認し、`IssueData` へ追加するメタ情報の抽出ロジックを実装。
2. リリース判定・領域判定ロジックを抽出または再構成し、新モジュール内の分類クラスへ実装。
3. 互換性種別・影響範囲・ステータス正規化のルールを定義し、分類処理とデータモデルを整備。
4. CLI エントリポイントを追加し、CSV 出力を生成するための配列整列・書き出し処理を実装。
5. 手動テスト（小規模データでの Dry-run）を行い、出力形式と正準値を確認。

## 成果物
- `run/canonical_issue_classifier.py`（仮称。API + CLI）
- `run/filter_jdk_issues.py` の最小改修（`IssueData` 拡張、必要な補助関数）
- 動作確認ログ（対話メモ）

## リスク・留意点
- XML に欠落フィールドが存在する可能性があるため、欠損値は正規化ルールで `"unknown"` などに一貫化する。
- 既存モジュールとの重複ロジックは将来的な統合余地を確保しつつ、今回の変更では過度なリファクタリングを避ける。

