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
        '''
    )

    parser.add_argument(
        '--file', '-f',
        default='../1.INPUT作成/3.INPUT/jdk_OpenJDK 21.0.6 Released.txt_output.txt',
        help='入力ファイルのパス（デフォルト: OpenJDK 21.0.6）'
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

    args = parser.parse_args()

    # 統計を読み込み
    print(f"ファイルを読み込み中: {args.file}")
    stats = load_and_analyze(args.file)

    # ID検索モード
    if args.id:
        print(f"\nIssue IDで検索: {args.id}")
        issue = stats.find_by_id(args.id)

        if issue:
            print(f"\n見つかりました:\n")
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
        else:
            print(f"\nIssue ID '{args.id}' は見つかりませんでした")
        return

    # キーワード検索モード
    if args.search:
        print(f"\nキーワードで検索: \"{args.search}\"")

        if args.search_fields:
            print(f"検索対象フィールド: {', '.join(args.search_fields)}")
            issues = stats.search_in_fields(args.search, fields=args.search_fields)
        else:
            print(f"検索対象フィールド: title, description, component")
            issues = stats.search_in_fields(args.search)

        print(f"\n結果: {len(issues)} 件\n")

        if issues:
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

    # 検索実行
    issues = stats.filter_issues(**filters)

    # 結果表示
    print(f"\n検索条件:")
    for key, value in filters.items():
        print(f"  {key}: {value}")

    print(f"\n結果: {len(issues)} 件\n")

    if args.verbose and issues:
        print("該当するissue:")
        for i, issue in enumerate(issues, 1):
            print(f"\n{i}. {issue.title}")
            print(f"   Priority: {issue.priority}")
            print(f"   Type: {issue.type}")
            print(f"   Component: {issue.component}")
            print(f"   OS: {issue.os if issue.os else '(未指定)'}")
    elif issues and not args.verbose:
        print("該当するissue:")
        for issue in issues:
            print(f"  - {issue.title}")


if __name__ == "__main__":
    main()
