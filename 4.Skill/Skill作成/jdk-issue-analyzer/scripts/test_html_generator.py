#!/usr/bin/env python3
"""
HTMLジェネレーターの統合テスト

すべての機能が正常に動作することを確認します。
"""

import os
from html_generator import HTMLGenerator, prepare_report_data
from jdk_issue_statistics import load_multiple_files


def test_html_generation():
    """HTMLレポート生成の統合テスト"""
    print("=" * 60)
    print("HTMLジェネレーター統合テスト")
    print("=" * 60)

    # テスト1: データ読み込み
    print("\n[テスト1] データ読み込み")
    versions = ['21.0.6']
    filepaths = ['../references/jdk_OpenJDK21_0_6_Released.txt']

    try:
        stats = load_multiple_files(filepaths)
        print(f"   ✅ {len(stats.issues)} 件のIssueを読み込み")
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return False

    # テスト2: HTMLジェネレーターの初期化
    print("\n[テスト2] HTMLジェネレーター初期化")
    try:
        generator = HTMLGenerator()
        print(f"   ✅ ジェネレーター初期化成功")
        print(f"   - Jinja2使用: {generator.use_jinja2}")
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return False

    # テスト3: レポートデータの準備
    print("\n[テスト3] レポートデータ準備")
    try:
        data = prepare_report_data(stats, versions)
        print(f"   ✅ データ準備成功")
        print(f"   - タイトル: {data['title']}")
        print(f"   - 総Issue数: {data['total_issues']}")
        print(f"   - 高優先度: {data['high_priority_count']}")
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return False

    # テスト4: HTMLレポート生成
    print("\n[テスト4] HTMLレポート生成")
    output_file = 'test_report.html'
    try:
        generator.generate(data, output_file)
        print(f"   ✅ レポート生成成功: {output_file}")
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return False

    # テスト5: 生成されたHTMLの検証
    print("\n[テスト5] 生成されたHTMLの検証")
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 基本チェック
        checks = [
            ('DOCTYPE宣言', '<!DOCTYPE html>' in html_content),
            ('タイトルタグ', '<title>JDK Issue Analysis Report' in html_content),
            ('Chart.js読み込み', 'chart.js' in html_content),
            ('JavaScriptデータ', 'const issuesData' in html_content),
            ('優先度統計', 'const priorityStats' in html_content),
            ('コンポーネント統計', 'const componentStats' in html_content),
            ('テーブルHTML', '<table id="issuesTable">' in html_content),
            ('フィルタHTML', 'id="searchInput"' in html_content),
            ('スクリプト完結', '</script>\n</body>\n</html>' in html_content),
        ]

        all_passed = True
        for name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {name}")
            if not result:
                all_passed = False

        # JSONデータが正しくエスケープされていないことを確認（HTMLエスケープされていない）
        if '&#34;' in html_content:
            print(f"   ❌ JSONデータがHTMLエスケープされています")
            all_passed = False
        else:
            print(f"   ✅ JSONデータが正しく埋め込まれています")

        if not all_passed:
            return False

    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return False

    # テスト6: カスタム設定
    print("\n[テスト6] カスタム設定のテスト")
    try:
        custom_config = {
            'title': 'カスタムテストレポート',
            'summary': 'これはテストです'
        }
        data = prepare_report_data(stats, versions, custom_config)
        generator.generate(data, 'test_custom_report.html')

        with open('test_custom_report.html', 'r', encoding='utf-8') as f:
            content = f.read()

        if 'カスタムテストレポート' in content and 'これはテストです' in content:
            print(f"   ✅ カスタム設定が正しく適用されました")
        else:
            print(f"   ❌ カスタム設定が適用されていません")
            return False
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return False

    # クリーンアップ
    print("\n[クリーンアップ]")
    try:
        os.remove(output_file)
        os.remove('test_custom_report.html')
        print("   ✅ テストファイルを削除")
    except:
        pass

    print("\n" + "=" * 60)
    print("✅ すべてのテストが成功しました！")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = test_html_generation()
    exit(0 if success else 1)
