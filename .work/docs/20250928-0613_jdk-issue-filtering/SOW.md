# SOW: OpenJDK 21.0.5 → 21.0.8 非互換調査用 機械除外ルール

版: 0.1 (ドラフト)
作成者: Codex CLI
日付: 20250928-0613

## 1. 背景 / 目的
- 案件の前提: 案件開始時点での OpenJDK バージョン (21.0.8) を採用。
- 非互換調査の基準: 調査開始時点は 21.0.5 であり、差分 (21.0.6/21.0.7/21.0.8) のうち、既存アプリケーション動作にクリティカルな影響が出うる Issue のみを抽出したい。
- 目的: 「壊れうる変更」に絞るため、不要な Issue を機械的に除外するルール（正準ルール）を定義し、再現性あるフィルタ出力を得る。

## 2. スコープ
- 対象バージョン: 21.0.6, 21.0.7, 21.0.8（差分は 21.0.5 → 21.0.8）
- 入力ファイル（ブロック区切りは `-----`）:
  - `run/jdk_OpenJDK 21.0.6 Released.txt_output.txt`
  - `run/jdk_OpenJDK 21.0.7 Released.txt_output.txt`
  - `run/jdk_OpenJDK 21.0.8 Released.txt_output.txt`
- 対象 OS: Windows 11（x64 想定）。ただし Issue 記載の `OS: generic` や `OS: windows_*` は潜在的に対象とみなす。
- 非対象（現時点）: Issue の JBS 追加取得・結合（後続の精度向上オプションとする）。

## 3. 成果物
- 機械フィルタ済み一覧: `.work/tmp/filtered_21.0.5_to_21.0.8.txt`
  - 「要レビュー候補（壊れうる可能性）」のみが出力されること。
  - 任意: 簡易サマリ（総件数/除外件数/残件数）。

## 4. 正準表現（入力の一意化）
- 判定キーはファイルブロック内の以下の正準ラベル/行で行う。
  - `Title:` `Type:` `Component:` `Description:` `OS:`
- 種別は正準値のみ使用し、同義語（例: Enhancement ≒ New Feature）は許容しない。基本は `Type: Bug` のみを対象にし、その他は除外する（後述）。

## 5. 機械除外ルール（第1段階）
除外ルールは大小文字を無視（case-insensitive）し、各ブロック（`-----` 区切り）単位で適用する。

1) 種別による一括除外（新機能・タスク）
   - 仕様: `Type:` が `Bug` 以外（`Enhancement`, `New Feature`, `Task`, `Sub-Task` 等）は除外。
   - 意図: 新機能追加・パラメータ追加（既存 API 動作変更なし）・管理/メタ作業は対象外。

2) ドキュメント・テスト専用の除外
   - 判定: `Title:`/`Description:` に以下の強キーワードを含む場合を除外。
     - `regtest|jtreg|TEST:|javadoc|man page|docs?\b|typo\b`
   - 意図: ドキュメントやテストだけの変更は動作非互換に直結しないため。

3) パフォーマンス改善のみの除外
   - 判定: `performance|\bperf\b|optimi[sz]e|microbench|\bbenchmark\b|speed up|faster`
   - 意図: 機能非互換ではなく性能改善のみの変更は対象外。

4) JVM の安定性/クラッシュ修正の除外
   - 判定: `\bcrash|\bhang\b|hs_err|core dump|SIG(SEGV|BUS|ILL)\b|\bassert(ion)?\b`
   - 意図: 既存バグの安定性改善は本調査の目的外。

5) プラットフォーム限定（非 Windows 系）除外
   - 判定: `\nOS:\s*(os_x|mac|macos|linux|solaris|aix|bsd)` を含むブロックを除外。
   - 取り扱い: `OS: windows_*` と `OS: generic` は残す（要調査対象）。

6) メタ作業（バージョンバンプ等）の除外
   - 判定: `Bump update version` / `Remove designator DEFAULT_PROMOTED_VERSION_PRE` を含むものを除外。
   - 意図: リリース工程のメタ変更であり非互換に無関係。

注意:
- 既存 API に実質的な挙動変更がない「オプション/パラメータの追加」は `Type: Enhancement` 側に寄るため (1) で概ね除外できる。本文に「add option|new flag|system property added」等がある場合はヒューリスティック除外を追加可能だが、初期版では過除外リスクを避け実装しない。

## 6. 重点的に残す（第2段階の人手レビュー対象）
機械除外を通過したブロックのうち、以下の兆候を含むものを優先レビュー。
- 互換性影響・挙動変更: `incompatib|behavior chang|spec chang|deprecat(e|ion).*remov|default.*chang|stricter|reject|forbid|fail.*by default`
- 例外/リンク時問題: `IllegalArgument|NullPointer|NoSuch(Method|Field)|LinkageError|VerifyError|ClassCast|ServiceLoader|module`
- I/O/時刻/セキュリティ既定: `TLS|cipher|algorithm|provider|CA|keystore|policy|permissions|tzdata|ZoneRules`
- Windows 依存: `OS: windows_` を含む、または Windows API/IME/フォント/HiDPI/プリンタ/ファイル/パス等の記載

（上記は優先度付けに使用。機械的に除外はしない）

## 7. 実装方式（最小実装 → 拡張）
段階的に YAGNI を遵守し、まず最小の AWK 実装で再現性ある出力を得る。

### 7.1 AWK ワンライナー（初期実装）
```
awk -v RS="-----\n" 'BEGIN{IGNORECASE=1}
  /\nType:[ ]*(Enhancement|New Feature|Task|Sub-Task)/{next}
  /\nOS:[ ]*(os_x|mac|macos|linux|solaris|aix|bsd)/{next}
  /(regtest|jtreg|TEST:|javadoc|man page|docs?\b|typo\b)/{next}
  /(performance|\bperf\b|optimi[sz]e|microbench|\bbenchmark\b|speed up|faster)/{next}
  /(\bcrash|\bhang\b|hs_err|core dump|SIG(SEGV|BUS|ILL)\b|\bassert(ion)?\b)/{next}
  /(Bump update version|Remove designator DEFAULT_PROMOTED_VERSION_PRE)/{next}
  {print $0; print "-----"}
' \
  "run/jdk_OpenJDK 21.0.6 Released.txt_output.txt" \
  "run/jdk_OpenJDK 21.0.7 Released.txt_output.txt" \
  "run/jdk_OpenJDK 21.0.8 Released.txt_output.txt" \
> .work/tmp/filtered_21.0.5_to_21.0.8.txt
```

### 7.2 Python 実装（任意・拡張）
- ルールを関数化し、将来の例外/上書きルールの調整を容易にする。
- JBS から補足メタデータ（issuetype/component/labels/os/cpu/fixVersion）を取得し、誤除外/取りこぼしを低減（本 SOW の範囲外）。

## 8. 検証方法 / 受け入れ基準
- 検証:
  - 既知のメタ Issue（Bump/Remove designator）の除外を確認。
  - `Type: Enhancement` を含むブロックが出力に含まれないことを確認。
  - `regtest/jtreg` を含むテスト専用 Issue が除外されることを確認。
  - 出力に `OS: generic` と `OS: windows_*` のブロックが残ることを確認。
- 受け入れ基準:
  - フィルタ後の残件が、手作業レビュー対象として現実的な件数に収束すること。
  - 再実行で同一入力から同一出力が得られること（再現性）。

## 9. リスク / 制約
- タイトル/本文ベースのヒューリスティックにより、少数の過除外/過残留の可能性。
- `OS: generic` はプラットフォーム横断のため必ずしも Windows 問題とは限らない（人手レビューで吸収）。
- `assert` という一般語の誤検知リスク（テスト文脈で出ることが多いが、上記 (2) と併せて影響は限定的）。

## 10. スケジュール / 工数（目安）
- 実装・初回出力: 0.5h
- サンプル検証と微調整（閾値/語彙の調整）: 0.5h

## 11. 承認依頼
- 本 SOW に記載の「機械除外ルール（§5）」および「実装方式（§7.1）」での実施可否をご確認ください。
- 承認後、`.work/tmp/filtered_21.0.5_to_21.0.8.txt` を生成し、簡易サマリとともに提出します。

