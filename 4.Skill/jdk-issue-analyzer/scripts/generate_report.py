#!/usr/bin/env python3
"""
JDK Issue HTMLレポート生成スクリプト

複数のJDKバージョンのIssueデータを分析し、インタラクティブなHTMLレポートを生成します。
"""

import sys
from typing import List, Dict, Any
from jdk_issue_statistics import load_multiple_files, IssueStatistics
from html_generator import HTMLGenerator, prepare_report_data


def generate_html_report(stats: IssueStatistics,
                        versions: List[str],
                        output_file: str = 'jdk_issue_report.html',
                        custom_config: Dict[str, Any] = None) -> None:
    """
    インタラクティブなHTMLレポートを生成（テンプレート方式）

    Args:
        stats: IssueStatistics オブジェクト
        versions: 分析対象のJDKバージョンリスト
        output_file: 出力ファイル名
        custom_config: カスタム設定（タイトル、説明、表示項目など）
    """
    # HTMLジェネレーターの初期化
    generator = HTMLGenerator()

    # レポートデータの準備
    data = prepare_report_data(stats, versions, custom_config)

    # HTMLレポートの生成
    generator.generate(data, output_file)

    print(f"✅ レポートを生成しました: {output_file}")


if __name__ == '__main__':
    # コマンドライン引数からバージョンとファイルパスを取得
    if len(sys.argv) < 2:
        print("使用方法: python generate_report.py <version1> [version2] [version3] ...")
        print("例: python generate_report.py 21.0.6 21.0.7 21.0.8")
        sys.exit(1)
    
    versions = sys.argv[1:]
    # Convert version format: 21.0.6 -> 21_0_6
    filepaths = []
    for v in versions:
        v_formatted = v.replace('.', '_')
        filepaths.append(f'../references/jdk_OpenJDK{v_formatted}_Released.txt')
    
    print(f"分析対象バージョン: {', '.join(versions)}")
    print(f"ファイル読み込み中...")
    
    stats = load_multiple_files(filepaths)
    print(f"✅ {len(stats.issues)} 件のIssueを読み込みました")
    
    generate_html_report(stats, versions)
