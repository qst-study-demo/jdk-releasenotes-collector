# JDK Release Notes Collector

## 目的

JDK 21のリリースノートを収集し、既存アプリケーションへの影響分析レポートを作成する

## プロジェクト構成

### 1. INPUT作成
[1.INPUT作成/メモ.md](1.INPUT作成/メモ.md)

まずはINPUTの整理。何をINPUTとして使うかを決める。

### 2. サマリ生成
[2.サマリ生成/メモ.md](2.サマリ生成/メモ.md)

INPUTから影響分析サマリを作る。テキストで作成。

### 3. レポート生成
[3.レポート生成/メモ.md](3.レポート生成/メモ.md)

テキストサマリからpptxを作成。あまり綺麗に出来なかった。

## AI活用内容

上記プロジェクト（1-3）におけるAI活用内容。

### プログラム作成
- Issueを取得し、ローカルにXML保存
- 除外プログラムを作成
- Issueを1ファイルにまとめる

### プログラム作成以外
- Issue除外条件の検討（壁打ち相手として）
- サマリ作成のためのプロンプトの作成（壁打ち相手として）
- サマリ作成（テキスト版）
- レポート作成（pptx）

---

## Claude Skill

### JDK Issue Analyzer Skill
[4.Skill作成/](4.Skill作成/)

Issue分析機能をAIサービスに組み込む。

**Skillとは:**
Claude Skill は、特定のタスクやワークフローを自動化・最適化するための機能モジュールです。Skill を Claude に組み込むことで、誰でも同じ手順で一貫した処理を実行できるようになります。

**実装内容:**
AI サービス上で以下の機能を提供します。
- Issue 分析の自動化：skill-creator によりレポート作成機能を Skill 化
- HTML レポート生成：Claude から直接、インタラクティブなレポートを生成
- 検索・フィルタリング機能：Issue の分類・絞り込みを支援

この Skill を導入することで、JDK の問題解析を効率化し、レポート作成を標準化できます。

作成例:  
共有チャットからはレポートが見れない  
https://claude.ai/share/58ddc0cc-2b22-4de9-9475-0c11fdf48db3  ※生成したレポートが見れないですね。。  
https://claude.ai/public/artifacts/3a99d00e-91bf-457e-bd84-46107c0e4753  
https://claude.ai/public/artifacts/b6e63b9e-817e-4545-99a8-e2eec10bcfb9  

まともに見るにはログイン必要  
https://claude.ai/chat/ebe271e8-0867-4bb8-a18e-de36711630ac  
