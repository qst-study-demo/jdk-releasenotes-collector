#!/usr/bin/env python3
"""
Issue検索用コマンドラインツール

このスクリプトは、JDK issueデータファイルから特定の条件に合致するissueを検索します。
複数の条件を組み合わせて（AND条件）、柔軟な検索が可能です。

主な機能:
----------
- Priority、Type、Component、OSなどの条件で検索
- 複数条件の組み合わせ（AND条件）
- 検索結果の件数表示
- --verbose オプションで詳細情報の表示

使い方:
------
基本的な使い方:
    python search_issues.py --priority P2 --os windows
    python search_issues.py --priority P3 --type Bug
    python search_issues.py --component hotspot --priority P4

短縮オプション:
    python search_issues.py -p P2 -o windows
    python search_issues.py -p P3 -t Bug -c hotspot

詳細表示:
    python search_issues.py --priority P3 --type Bug --verbose
    python search_issues.py -p P3 -t Bug -v

別のファイルを検索:
    python search_issues.py -p P2 -o windows -f "path/to/issues.txt"

複数ファイルを同時に検索:
    python search_issues.py -p P2 -f "file1.txt" "file2.txt" "file3.txt"
    python search_issues.py --search "Windows" -f "jdk_21.0.6.txt" "jdk_21.0.7.txt"

検索条件:
--------
以下のオプションを組み合わせて検索できます:
    --priority, -p  : 優先度（P2, P3, P4, P5など）
    --type, -t      : タイプ（Bug, Sub-taskなど）
    --component, -c : コンポーネント（hotspot, security-libsなど）
    --os, -o        : OS（windows, generic, linuxなど）
    --file, -f      : 入力ファイルのパス
    --verbose, -v   : 詳細情報を表示

使用例:
------
1. Priority=P2かつOS=windows:
   $ python search_issues.py --priority P2 --os windows

2. Priority=P3のBug:
   $ python search_issues.py --priority P3 --type Bug

3. hotspotコンポーネントのP4 issue:
   $ python search_issues.py --component hotspot --priority P4

4. security-libsのP3 Bugを詳細表示:
   $ python search_issues.py -p P3 -t Bug -c security-libs --verbose

5. 別ファイルから検索:
   $ python search_issues.py -p P2 -f "jdk_OpenJDK 21.0.7 Released.txt_output.txt"

6. 複数ファイルを同時に検索:
   $ python search_issues.py -p P2 -f "jdk_21.0.6.txt" "jdk_21.0.7.txt" "jdk_21.0.8.txt"
   $ python search_issues.py --search "security" -f "jdk_21.0.6.txt" "jdk_21.0.7.txt"

7. 複数ファイルを統合して検索:
   $ python search_issues.py -p P2 --merge -f "jdk_21.0.6.txt" "jdk_21.0.7.txt" "jdk_21.0.8.txt"

8. 統計情報の表示:
   $ python search_issues.py -p P2 --stats -f "jdk_21.0.6.txt"

9. 結果をグループ化して表示:
   $ python search_issues.py -p P2 --group-by priority -f "jdk_21.0.6.txt" "jdk_21.0.7.txt"
   $ python search_issues.py --search "Windows" --group-by component -f "jdk_21.0.7.txt"

出力形式:
--------
通常モード:
    検索条件:
      priority: P3
      type: Bug

    結果: 16 件

    該当するissue:
      - [JDK-8319973] AArch64: Save and restore FPCR...
      - [JDK-8320192] SHAKE256 does not work correctly...
      ...

詳細モード（--verbose）:
    1. [JDK-8319973] AArch64: Save and restore FPCR...
       Priority: P3
       Type: Bug
       Component: hotspot
       OS: generic
    ...

注意事項:
--------
- 最低1つの検索条件を指定する必要があります
- 複数の条件を指定した場合、すべての条件を満たすissue（AND条件）が返されます
- 文字列の比較は大文字小文字を区別しません（P3とp3は同じ）
"""

import argparse
from jdk_issue_statistics import load_and_analyze, load_multiple_files
from typing import List
from jdk_issue_statistics import Issue


def display_statistics(stats, title="統計情報"):
    """統計サマリーを表示"""
    print(f"\n{'=' * 80}")
    print(f"{title}")
    print('=' * 80)

    print(f"\n総Issue数: {len(stats.issues)} 件\n")

    # 優先度別統計
    priority_stats = stats.get_priority_stats()
    print("📊 優先度別:")
    priority_order = ['P1', 'P2', 'P3', 'P4', 'P5']
    for priority in priority_order:
        if priority in priority_stats:
            print(f"  {priority}: {priority_stats[priority]} 件")
    # 順序外の優先度
    for priority, count in sorted(priority_stats.items()):
        if priority not in priority_order:
            print(f"  {priority}: {count} 件")

    # タイプ別統計
    type_stats = stats.get_type_stats()
    print("\n📋 タイプ別:")
    for issue_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {issue_type}: {count} 件")

    # コンポーネント別統計（上位10件）
    component_stats = stats.get_component_stats()
    print("\n🔧 コンポーネント別（上位10件）:")
    for component, count in sorted(component_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {component}: {count} 件")

    # OS別統計
    os_stats = stats.get_os_stats()
    if os_stats:
        print("\n💻 OS別:")
        for os, count in sorted(os_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {os}: {count} 件")

    print('=' * 80)


def group_issues_by(issues: List[Issue], group_by: str):
    """Issueをグループ化"""
    groups = {}
    for issue in issues:
        if group_by == 'priority':
            key = issue.priority or '未指定'
        elif group_by == 'type':
            key = issue.type or '未指定'
        elif group_by == 'component':
            key = issue.component or '未指定'
        else:
            key = '未指定'

        if key not in groups:
            groups[key] = []
        groups[key].append(issue)

    return groups


def display_grouped_issues(groups: dict, group_by: str, verbose: bool):
    """グループ化されたIssueを表示"""
    # ソート順を決定
    if group_by == 'priority':
        priority_order = ['P1', 'P2', 'P3', 'P4', 'P5', '未指定']
        sorted_keys = sorted(groups.keys(),
                            key=lambda x: priority_order.index(x) if x in priority_order else 999)
    else:
        # 件数の多い順
        sorted_keys = sorted(groups.keys(), key=lambda x: len(groups[x]), reverse=True)

    for key in sorted_keys:
        issues = groups[key]
        print(f"\n{'=' * 80}")
        print(f"{group_by.capitalize()}: {key} ({len(issues)} 件)")
        print('=' * 80)

        if verbose:
            for i, issue in enumerate(issues, 1):
                print(f"\n{i}. {issue.title}")
                print(f"   ID: {issue.issue_id}")
                print(f"   Priority: {issue.priority}")
                print(f"   Type: {issue.type}")
                print(f"   Component: {issue.component}")
                print(f"   OS: {issue.os if issue.os else '(未指定)'}")
        else:
            for issue in issues:
                print(f"  - [{issue.issue_id}] {issue.title}")


def main():
    """
    メイン関数

    コマンドライン引数をパースし、指定された条件でissueを検索して結果を表示します。

    処理フロー:
        1. コマンドライン引数のパース
        2. フィルタ条件の構築
        3. issueファイルの読み込みと統計オブジェクトの作成
        4. フィルタリングの実行
        5. 結果の表示（通常モードまたは詳細モード）

    終了コード:
        0: 正常終了（検索条件が指定され、検索が実行された）
        1: エラー（検索条件が指定されていない）
    """
    parser = argparse.ArgumentParser(
        description='JDK Issueを検索します',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  # Issue IDで検索
  python search_issues.py --id JDK-8320192
  python search_issues.py --id 8320192  # JDK-プレフィックス省略可能

  # キーワードで本文を検索
  python search_issues.py --search "Windows 11"
  python search_issues.py --search "platform" --verbose

  # Priority=P2かつOS=windows
  python search_issues.py --priority P2 --os windows

  # Priority=P3のBug
  python search_issues.py --priority P3 --type Bug

  # hotspotコンポーネントのP4
  python search_issues.py --component hotspot --priority P4

  # 詳細表示付き
  python search_issues.py --priority P3 --type Bug --verbose

  # 複数ファイルを同時に検索
  python search_issues.py -p P2 -f "jdk_21.0.6.txt" "jdk_21.0.7.txt" "jdk_21.0.8.txt"
  python search_issues.py --search "security" -f "jdk_21.0.6.txt" "jdk_21.0.7.txt"

  # 複数ファイルを統合して検索
  python search_issues.py -p P2 --merge -f "jdk_21.0.6.txt" "jdk_21.0.7.txt" "jdk_21.0.8.txt"

  # 統計情報の表示
  python search_issues.py -p P2 --stats -f "jdk_21.0.6.txt"

  # 結果をグループ化して表示
  python search_issues.py -p P2 --group-by priority -f "jdk_21.0.6.txt" "jdk_21.0.7.txt"
  python search_issues.py --search "Windows" --group-by component -f "jdk_21.0.7.txt"
        '''
    )

    parser.add_argument(
        '--file', '-f',
        nargs='+',
        default=['../../../1.INPUT作成/3.INPUT/jdk_OpenJDK 21.0.6 Released.txt_output.txt'],
        help='入力ファイルのパス（複数指定可能）（デフォルト: OpenJDK 21.0.6）'
    )
    parser.add_argument('--id', '-i', help='Issue ID (例: JDK-8320192, 8320192)')
    parser.add_argument('--search', '-s', help='キーワードで本文を検索 (例: "Windows 11", "platform")')
    parser.add_argument('--search-fields', nargs='+',
                       help='検索対象フィールド (デフォルト: title description component)')
    parser.add_argument('--priority', '-p', help='Priority (例: P2, P3, P4)')
    parser.add_argument('--type', '-t', help='Type (例: Bug, Sub-task)')
    parser.add_argument('--component', '-c', help='Component (例: hotspot, security-libs)')
    parser.add_argument('--os', '-o', help='OS (例: windows, generic, linux)')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細情報を表示')
    parser.add_argument('--merge', '-m', action='store_true', help='複数ファイルを統合して処理（ファイル別に表示しない）')
    parser.add_argument('--stats', action='store_true', help='統計サマリーを表示')
    parser.add_argument('--group-by', '-g', choices=['priority', 'type', 'component'],
                       help='結果をグループ化して表示 (priority, type, component)')

    args = parser.parse_args()

    # 複数ファイルの処理
    files = args.file if isinstance(args.file, list) else [args.file]

    # マージモードの場合、全ファイルを統合して読み込み
    if args.merge and len(files) > 1:
        print(f"ファイルを統合読み込み中: {len(files)} ファイル")
        for f in files:
            print(f"  - {f}")
        try:
            merged_stats = load_multiple_files(files)
            all_stats = [("統合データ", merged_stats)]
        except Exception as e:
            print(f"エラー: ファイルの読み込みに失敗しました: {e}")
            return
    else:
        # 通常モード：各ファイルを個別に読み込み
        all_stats = []
        for file_path in files:
            print(f"ファイルを読み込み中: {file_path}")
            try:
                stats = load_and_analyze(file_path)
                all_stats.append((file_path, stats))
            except Exception as e:
                print(f"エラー: {file_path} の読み込みに失敗しました: {e}")
                continue

        if not all_stats:
            print("エラー: 有効なファイルが読み込めませんでした")
            return

    # ID検索モード
    if args.id:
        print(f"\nIssue IDで検索: {args.id}\n")
        found = False

        for file_path, stats in all_stats:
            issue = stats.find_by_id(args.id)

            if issue:
                found = True
                print(f"[{file_path}]")
                print(f"見つかりました:\n")
                print(f"Title: {issue.title}")
                print(f"Priority: {issue.priority}")
                print(f"Type: {issue.type}")
                print(f"Component: {issue.component}")
                print(f"OS: {issue.os if issue.os else '(未指定)'}")

                if args.verbose and issue.description:
                    print(f"\nDescription:")
                    # 最初の500文字まで表示
                    desc = issue.description[:500]
                    print(f"{desc}")
                    if len(issue.description) > 500:
                        print(f"... (残り {len(issue.description) - 500} 文字)")
                print()

        if not found:
            print(f"Issue ID '{args.id}' は見つかりませんでした")
        return

    # キーワード検索モード
    if args.search:
        print(f"\nキーワードで検索: \"{args.search}\"")

        if args.search_fields:
            print(f"検索対象フィールド: {', '.join(args.search_fields)}")
        else:
            print(f"検索対象フィールド: title, description, component")

        # 統計モード
        if args.stats:
            for file_path, stats in all_stats:
                title = f"統計情報: {file_path}" if len(all_stats) > 1 else "統計情報"
                display_statistics(stats, title)
            return

        # 検索実行
        all_issues = []
        total_issues = 0

        for file_path, stats in all_stats:
            if args.search_fields:
                issues = stats.search_in_fields(args.search, fields=args.search_fields)
            else:
                issues = stats.search_in_fields(args.search)

            if issues:
                all_issues.extend(issues)
                total_issues += len(issues)

                # グループ化モードでない場合のみファイル別に表示
                if not args.group_by:
                    print(f"\n[{file_path}]")
                    print(f"結果: {len(issues)} 件\n")

                    if args.verbose:
                        print("該当するissue:\n")
                        for i, issue in enumerate(issues, 1):
                            print(f"{i}. {issue.title}")
                            print(f"   ID: {issue.issue_id}")
                            print(f"   Priority: {issue.priority}, Type: {issue.type}")
                            print(f"   Component: {issue.component}")

                            # キーワード周辺のテキストを表示
                            if issue.description:
                                keyword_lower = args.search.lower()
                                desc_lower = issue.description.lower()
                                idx = desc_lower.find(keyword_lower)
                                if idx >= 0:
                                    start = max(0, idx - 60)
                                    end = min(len(issue.description), idx + len(args.search) + 80)
                                    snippet = issue.description[start:end].replace('\n', ' ')
                                    print(f"   Context: ...{snippet}...")
                            print()
                    else:
                        print("該当するissue:")
                        for issue in issues:
                            print(f"  - {issue.issue_id}: {issue.title}")
                        print()

        # グループ化モード
        if args.group_by and all_issues:
            print(f"\n結果を {args.group_by} でグループ化:\n")
            groups = group_issues_by(all_issues, args.group_by)
            display_grouped_issues(groups, args.group_by, args.verbose)

        # 結果サマリー
        if total_issues == 0:
            print(f"\nキーワード \"{args.search}\" に一致するissueは見つかりませんでした")
        else:
            print(f"\n=== 合計: {total_issues} 件 ===")

        return

    # フィルタ条件を構築
    filters = {}
    if args.priority:
        filters['priority'] = args.priority
    if args.type:
        filters['type'] = args.type
    if args.component:
        filters['component'] = args.component
    if args.os:
        filters['os'] = args.os

    if not filters:
        parser.print_help()
        print("\n\nエラー: 最低1つの検索条件（--id、--search、または --priority/--type/--component/--os）を指定してください")
        return

    # 結果表示
    print(f"\n検索条件:")
    for key, value in filters.items():
        print(f"  {key}: {value}")

    # 統計モード: 全ファイルの統計を表示
    if args.stats:
        for file_path, stats in all_stats:
            title = f"統計情報: {file_path}" if len(all_stats) > 1 else "統計情報"
            display_statistics(stats, title)
        return

    # 検索実行して結果を収集
    all_issues = []
    total_issues = 0

    for file_path, stats in all_stats:
        issues = stats.filter_issues(**filters)
        if issues:
            all_issues.extend(issues)
            total_issues += len(issues)

            # グループ化モードでない場合のみファイル別に表示
            if not args.group_by:
                print(f"\n[{file_path}]")
                print(f"結果: {len(issues)} 件\n")

                if args.verbose:
                    print("該当するissue:")
                    for i, issue in enumerate(issues, 1):
                        print(f"\n{i}. {issue.title}")
                        print(f"   Priority: {issue.priority}")
                        print(f"   Type: {issue.type}")
                        print(f"   Component: {issue.component}")
                        print(f"   OS: {issue.os if issue.os else '(未指定)'}")
                else:
                    print("該当するissue:")
                    for issue in issues:
                        print(f"  - {issue.title}")
                print()

    # グループ化モード
    if args.group_by and all_issues:
        print(f"\n結果を {args.group_by} でグループ化:\n")
        groups = group_issues_by(all_issues, args.group_by)
        display_grouped_issues(groups, args.group_by, args.verbose)

    # 結果サマリー
    if total_issues == 0:
        print(f"\n指定された条件に一致するissueは見つかりませんでした")
    else:
        print(f"\n=== 合計: {total_issues} 件 ===")


if __name__ == "__main__":
    main()
