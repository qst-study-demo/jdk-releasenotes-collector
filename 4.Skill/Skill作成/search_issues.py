#!/usr/bin/env python3
"""
Issue検索用コマンドラインツール

このスクリプトは、JDK issueデータファイルから特定の条件に合致するissueを検索します。
複数の条件を組み合わせて（AND条件）、柔軟な検索が可能です。

主な機能:
----------
- Priority、Type、Component、OSなどの条件で検索
- 複数条件の組み合わせ（AND条件）
- 複数ファイルの同時検索
- 検索結果の統計情報表示（--stats）
- 検索結果のグループ化（--group-by）
- 検索結果のソート（--sort）
- 表示件数制限（--limit）
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
    python search_issues.py --search "Windows" -f *.txt

検索条件:
--------
以下のオプションを組み合わせて検索できます:
    --priority, -p  : 優先度（P2, P3, P4, P5など）
    --type, -t      : タイプ（Bug, Sub-taskなど）
    --component, -c : コンポーネント（hotspot, security-libsなど）
    --os, -o        : OS（windows, generic, linuxなど）
    --file, -f      : 入力ファイルのパス（複数指定可能）
    --verbose, -v   : 詳細情報を表示
    --stats         : 統計情報を表示
    --group-by, -g  : 結果をグループ化（priority/type/component/os/file）
    --sort          : 結果をソート（priority/type/component/os）
    --limit, -l     : 表示件数を制限

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

6. 複数ファイルから検索:
   $ python search_issues.py -p P2 -f "file1.txt" "file2.txt" "file3.txt"
   $ python search_issues.py --search "Windows" -f jdk_*.txt

7. 統計情報付きで検索:
   $ python search_issues.py --os windows --stats

8. 優先度別にグループ化:
   $ python search_issues.py -p P3 -t Bug --group-by priority --verbose

9. 優先度順にソートして上位10件を表示:
   $ python search_issues.py --os windows --sort priority --limit 10

10. コンポーネント別にグループ化して統計表示:
    $ python search_issues.py -p P2 -p P3 --group-by component --stats

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
from jdk_issue_statistics import load_and_analyze
from collections import defaultdict


def print_statistics(issues_with_files):
    """
    検索結果の統計情報を表示

    Args:
        issues_with_files: (file_path, issue)のタプルのリスト
    """
    if not issues_with_files:
        return

    print("\n" + "=" * 80)
    print("📊 統計情報")
    print("=" * 80)

    # 優先度別統計
    priority_stats = defaultdict(int)
    for _, issue in issues_with_files:
        priority = issue.priority or '未指定'
        priority_stats[priority] += 1

    print("\n優先度別:")
    priority_order = ['P1', 'P2', 'P3', 'P4', 'P5', '未指定']
    for priority in priority_order:
        if priority in priority_stats:
            count = priority_stats[priority]
            print(f"  {priority}: {count} 件")

    # タイプ別統計
    type_stats = defaultdict(int)
    for _, issue in issues_with_files:
        issue_type = issue.type or '未指定'
        type_stats[issue_type] += 1

    print("\nタイプ別:")
    for issue_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {issue_type}: {count} 件")

    # コンポーネント別統計（上位10件）
    component_stats = defaultdict(int)
    for _, issue in issues_with_files:
        component = issue.component or '未指定'
        component_stats[component] += 1

    print("\nコンポーネント別 (上位10件):")
    for component, count in sorted(component_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {component}: {count} 件")

    # OS別統計
    os_stats = defaultdict(int)
    for _, issue in issues_with_files:
        os = issue.os or '未指定'
        os_stats[os] += 1

    print("\nOS別:")
    for os, count in sorted(os_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {os}: {count} 件")

    # ファイル別統計
    file_stats = defaultdict(int)
    for file_path, _ in issues_with_files:
        file_stats[file_path] += 1

    print("\nファイル別:")
    for file_path, count in sorted(file_stats.items(), key=lambda x: x[1], reverse=True):
        import os
        filename = os.path.basename(file_path)
        print(f"  {filename}: {count} 件")

    print("=" * 80)


def group_issues(issues_with_files, group_by):
    """
    検索結果をグループ化

    Args:
        issues_with_files: (file_path, issue)のタプルのリスト
        group_by: グループ化のキー ('priority', 'type', 'component', 'os', 'file')

    Returns:
        グループ化された辞書 {key: [(file_path, issue), ...]}
    """
    groups = defaultdict(list)

    for file_path, issue in issues_with_files:
        if group_by == 'priority':
            key = issue.priority or '未指定'
        elif group_by == 'type':
            key = issue.type or '未指定'
        elif group_by == 'component':
            key = issue.component or '未指定'
        elif group_by == 'os':
            key = issue.os or '未指定'
        elif group_by == 'file':
            import os
            key = os.path.basename(file_path)
        else:
            key = '未分類'

        groups[key].append((file_path, issue))

    return groups


def sort_issues(issues_with_files, sort_by):
    """
    検索結果をソート

    Args:
        issues_with_files: (file_path, issue)のタプルのリスト
        sort_by: ソートのキー ('priority', 'type', 'component', 'os')

    Returns:
        ソートされたリスト
    """
    if sort_by == 'priority':
        priority_order = {'P1': 1, 'P2': 2, 'P3': 3, 'P4': 4, 'P5': 5}
        return sorted(issues_with_files,
                     key=lambda x: priority_order.get(x[1].priority, 999))
    elif sort_by == 'type':
        return sorted(issues_with_files, key=lambda x: x[1].type or '未指定')
    elif sort_by == 'component':
        return sorted(issues_with_files, key=lambda x: x[1].component or '未指定')
    elif sort_by == 'os':
        return sorted(issues_with_files, key=lambda x: x[1].os or '未指定')
    else:
        return issues_with_files


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

  # 複数ファイルから検索
  python search_issues.py -p P2 -f "file1.txt" "file2.txt" "file3.txt"
  python search_issues.py --search "Windows" -f jdk_*.txt

  # 統計情報付きで検索
  python search_issues.py --os windows --stats

  # 優先度別にグループ化
  python search_issues.py -t Bug --group-by priority --verbose

  # 優先度順にソートして上位10件
  python search_issues.py --os windows --sort priority --limit 10

  # コンポーネント別にグループ化して統計表示
  python search_issues.py -p P3 --group-by component --stats
        '''
    )

    parser.add_argument(
        '--file', '-f',
        nargs='+',
        default=['../1.INPUT作成/3.INPUT/jdk_OpenJDK 21.0.6 Released.txt_output.txt'],
        help='入力ファイルのパス（複数指定可能、デフォルト: OpenJDK 21.0.6）'
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
    parser.add_argument('--stats', action='store_true', help='検索結果の統計情報を表示')
    parser.add_argument('--group-by', '-g',
                       choices=['priority', 'type', 'component', 'os', 'file'],
                       help='結果をグループ化 (priority/type/component/os/file)')
    parser.add_argument('--sort',
                       choices=['priority', 'type', 'component', 'os'],
                       help='結果をソート (priority/type/component/os)')
    parser.add_argument('--limit', '-l', type=int, help='表示件数を制限')

    args = parser.parse_args()

    # 複数ファイルの統計を読み込み
    files = args.file if isinstance(args.file, list) else [args.file]
    print(f"ファイルを読み込み中: {len(files)} 件")
    for f in files:
        print(f"  - {f}")

    # 各ファイルから統計を読み込む
    all_stats = []
    for file_path in files:
        try:
            stats = load_and_analyze(file_path)
            all_stats.append((file_path, stats))
        except Exception as e:
            print(f"警告: {file_path} の読み込みに失敗しました: {e}")

    if not all_stats:
        print("エラー: 有効なファイルが読み込めませんでした")
        return

    # ID検索モード
    if args.id:
        print(f"\nIssue IDで検索: {args.id}")
        found = False
        for file_path, stats in all_stats:
            issue = stats.find_by_id(args.id)
            if issue:
                if not found:
                    print(f"\n見つかりました:\n")
                found = True
                print(f"ファイル: {file_path}")
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
            print(f"\nIssue ID '{args.id}' は見つかりませんでした")
        return

    # キーワード検索モード
    if args.search:
        print(f"\nキーワードで検索: \"{args.search}\"")

        if args.search_fields:
            print(f"検索対象フィールド: {', '.join(args.search_fields)}")
        else:
            print(f"検索対象フィールド: title, description, component")

        # 全ファイルから検索結果を収集
        all_issues = []
        for file_path, stats in all_stats:
            if args.search_fields:
                issues = stats.search_in_fields(args.search, fields=args.search_fields)
            else:
                issues = stats.search_in_fields(args.search)

            # 各issueにファイルパス情報を追加
            for issue in issues:
                all_issues.append((file_path, issue))

        print(f"\n結果: {len(all_issues)} 件\n")

        if all_issues:
            # 統計表示
            if args.stats:
                print_statistics(all_issues)
                print()

            # ソート
            if args.sort:
                all_issues = sort_issues(all_issues, args.sort)

            # 表示件数制限
            display_issues = all_issues[:args.limit] if args.limit else all_issues
            if args.limit and len(all_issues) > args.limit:
                print(f"(最初の{args.limit}件を表示)\n")

            # グループ化表示
            if args.group_by:
                groups = group_issues(display_issues, args.group_by)
                # グループをソート
                if args.group_by == 'priority':
                    priority_order = ['P1', 'P2', 'P3', 'P4', 'P5', '未指定']
                    sorted_groups = sorted(groups.items(),
                                         key=lambda x: priority_order.index(x[0]) if x[0] in priority_order else 999)
                else:
                    sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)

                for group_key, group_issues in sorted_groups:
                    print(f"\n{'=' * 80}")
                    print(f"{args.group_by.upper()}: {group_key} ({len(group_issues)} 件)")
                    print('=' * 80)

                    if args.verbose:
                        for i, (file_path, issue) in enumerate(group_issues, 1):
                            print(f"\n{i}. {issue.title}")
                            print(f"   ファイル: {file_path}")
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
                    else:
                        for file_path, issue in group_issues:
                            print(f"  - {issue.issue_id}: {issue.title}")
            else:
                # 通常表示
                if args.verbose:
                    print("該当するissue:\n")
                    for i, (file_path, issue) in enumerate(display_issues, 1):
                        print(f"{i}. {issue.title}")
                        print(f"   ファイル: {file_path}")
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
                    for file_path, issue in display_issues:
                        print(f"  - {issue.issue_id}: {issue.title} (from {file_path})")
        else:
            print(f"キーワード \"{args.search}\" に一致するissueは見つかりませんでした")

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

    # 全ファイルから検索結果を収集
    all_issues = []
    for file_path, stats in all_stats:
        issues = stats.filter_issues(**filters)
        # 各issueにファイルパス情報を追加
        for issue in issues:
            all_issues.append((file_path, issue))

    # 結果表示
    print(f"\n検索条件:")
    for key, value in filters.items():
        print(f"  {key}: {value}")

    print(f"\n結果: {len(all_issues)} 件\n")

    if all_issues:
        # 統計表示
        if args.stats:
            print_statistics(all_issues)
            print()

        # ソート
        if args.sort:
            all_issues = sort_issues(all_issues, args.sort)

        # 表示件数制限
        display_issues = all_issues[:args.limit] if args.limit else all_issues
        if args.limit and len(all_issues) > args.limit:
            print(f"(最初の{args.limit}件を表示)\n")

        # グループ化表示
        if args.group_by:
            groups = group_issues(display_issues, args.group_by)
            # グループをソート
            if args.group_by == 'priority':
                priority_order = ['P1', 'P2', 'P3', 'P4', 'P5', '未指定']
                sorted_groups = sorted(groups.items(),
                                     key=lambda x: priority_order.index(x[0]) if x[0] in priority_order else 999)
            else:
                sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)

            for group_key, group_issues in sorted_groups:
                print(f"\n{'=' * 80}")
                print(f"{args.group_by.upper()}: {group_key} ({len(group_issues)} 件)")
                print('=' * 80)

                if args.verbose:
                    for i, (file_path, issue) in enumerate(group_issues, 1):
                        print(f"\n{i}. {issue.title}")
                        print(f"   ファイル: {file_path}")
                        print(f"   Priority: {issue.priority}")
                        print(f"   Type: {issue.type}")
                        print(f"   Component: {issue.component}")
                        print(f"   OS: {issue.os if issue.os else '(未指定)'}")

                        # 説明の一部を表示
                        if issue.description:
                            desc = issue.description.replace('\n', ' ').strip()
                            if len(desc) > 200:
                                desc = desc[:200] + '...'
                            print(f"   説明: {desc}")
                else:
                    for file_path, issue in group_issues:
                        print(f"  - {issue.title}")
        else:
            # 通常表示
            if args.verbose:
                print("該当するissue:")
                for i, (file_path, issue) in enumerate(display_issues, 1):
                    print(f"\n{i}. {issue.title}")
                    print(f"   ファイル: {file_path}")
                    print(f"   Priority: {issue.priority}")
                    print(f"   Type: {issue.type}")
                    print(f"   Component: {issue.component}")
                    print(f"   OS: {issue.os if issue.os else '(未指定)'}")

                    # 説明の一部を表示
                    if issue.description:
                        desc = issue.description.replace('\n', ' ').strip()
                        if len(desc) > 200:
                            desc = desc[:200] + '...'
                        print(f"   説明: {desc}")
            else:
                print("該当するissue:")
                for file_path, issue in display_issues:
                    print(f"  - {issue.title} (from {file_path})")


if __name__ == "__main__":
    main()
