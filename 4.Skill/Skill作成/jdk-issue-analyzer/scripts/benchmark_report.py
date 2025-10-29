#!/usr/bin/env python3
"""
HTMLレポート生成のベンチマーク

テンプレート方式の性能を測定します。
"""

import time
from jdk_issue_statistics import load_multiple_files
from generate_report import generate_html_report


def benchmark():
    """レポート生成のベンチマーク"""
    versions = ['21.0.6', '21.0.7', '21.0.8']
    filepaths = []
    for v in versions:
        v_formatted = v.replace('.', '_')
        filepaths.append(f'../references/jdk_OpenJDK{v_formatted}_Released.txt')

    print("=" * 60)
    print("HTMLレポート生成ベンチマーク")
    print("=" * 60)
    print(f"\n対象バージョン: {', '.join(versions)}")

    # データ読み込み
    print("\n[1] データ読み込み中...")
    start_time = time.time()
    stats = load_multiple_files(filepaths)
    load_time = time.time() - start_time
    print(f"   ✅ {len(stats.issues)} 件のIssueを読み込み完了 ({load_time:.3f}秒)")

    # HTML生成（初回）
    print("\n[2] HTMLレポート生成（初回）...")
    start_time = time.time()
    generate_html_report(stats, versions, 'benchmark_report_1.html')
    gen_time_1 = time.time() - start_time
    print(f"   ✅ 生成完了 ({gen_time_1:.3f}秒)")

    # HTML生成（2回目 - テンプレートキャッシュの効果を確認）
    print("\n[3] HTMLレポート生成（2回目）...")
    start_time = time.time()
    generate_html_report(stats, versions, 'benchmark_report_2.html')
    gen_time_2 = time.time() - start_time
    print(f"   ✅ 生成完了 ({gen_time_2:.3f}秒)")

    # HTML生成（3回目）
    print("\n[4] HTMLレポート生成（3回目）...")
    start_time = time.time()
    generate_html_report(stats, versions, 'benchmark_report_3.html')
    gen_time_3 = time.time() - start_time
    print(f"   ✅ 生成完了 ({gen_time_3:.3f}秒)")

    # 結果サマリー
    print("\n" + "=" * 60)
    print("ベンチマーク結果サマリー")
    print("=" * 60)
    print(f"Issue総数:        {len(stats.issues)} 件")
    print(f"データ読み込み時間: {load_time:.3f}秒")
    print(f"HTML生成時間（初回）: {gen_time_1:.3f}秒")
    print(f"HTML生成時間（2回目）: {gen_time_2:.3f}秒")
    print(f"HTML生成時間（3回目）: {gen_time_3:.3f}秒")
    print(f"平均生成時間:      {(gen_time_1 + gen_time_2 + gen_time_3) / 3:.3f}秒")
    print()

    # 性能指標
    issues_per_second = len(stats.issues) / gen_time_2
    print(f"処理速度:         {issues_per_second:.0f} Issues/秒")
    print()

    # クリーンアップ
    import os
    for i in range(1, 4):
        try:
            os.remove(f'benchmark_report_{i}.html')
        except:
            pass

    print("✅ ベンチマーク完了")


if __name__ == '__main__':
    benchmark()
