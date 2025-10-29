#!/usr/bin/env python3
"""
HTMLテンプレートジェネレーター

テンプレートを使用してHTMLレポートを高速生成します。
"""

import json
import os
from typing import Dict, List, Any
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


class HTMLGenerator:
    """HTMLレポートを効率的に生成するジェネレータークラス"""

    def __init__(self, template_dir: str = None):
        """
        初期化

        Args:
            template_dir: テンプレートディレクトリのパス（省略時は自動検出）
        """
        if template_dir is None:
            # スクリプトのディレクトリから相対パスでテンプレートディレクトリを取得
            script_dir = Path(__file__).parent
            template_dir = script_dir.parent / 'templates'

        self.template_dir = Path(template_dir)

        if JINJA2_AVAILABLE:
            # Jinja2環境の設定
            # autoescapeは無効化（JSONデータをそのまま埋め込むため）
            self.env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=False
            )
            self.use_jinja2 = True
        else:
            # Jinja2が利用できない場合は単純な置換を使用
            self.use_jinja2 = False
            self._load_template()

    def _load_template(self):
        """テンプレートを読み込む（Jinja2未使用時）"""
        template_path = self.template_dir / 'report_template.html'
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = f.read()

    def generate(self, data: Dict[str, Any], output_file: str) -> None:
        """
        HTMLレポートを生成

        Args:
            data: テンプレートに渡すデータ
            output_file: 出力ファイルパス
        """
        if self.use_jinja2:
            self._generate_with_jinja2(data, output_file)
        else:
            self._generate_with_replace(data, output_file)

    def _generate_with_jinja2(self, data: Dict[str, Any], output_file: str) -> None:
        """Jinja2を使用してHTMLを生成"""
        template = self.env.get_template('report_template.html')
        html_content = template.render(**data)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_with_replace(self, data: Dict[str, Any], output_file: str) -> None:
        """単純な置換を使用してHTMLを生成（Jinja2未使用時）"""
        html_content = self.template

        # プレースホルダーを置換
        for key, value in data.items():
            placeholder = f'{{{{ {key} }}}}'

            # 値をJSON形式に変換（必要な場合）
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            html_content = html_content.replace(placeholder, str(value))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)


def generate_type_options(type_stats: Dict[str, int]) -> str:
    """タイプフィルタのオプションを生成"""
    options = []
    for type_name in sorted(type_stats.keys()):
        options.append(f'<option value="{type_name}">{type_name}</option>')
    return '\n'.join(options)


def generate_component_options(component_stats: Dict[str, int]) -> str:
    """コンポーネントフィルタのオプションを生成"""
    options = []
    # 上位15コンポーネントのみ表示
    top_components = sorted(component_stats.items(), key=lambda x: x[1], reverse=True)[:15]
    for component, _ in top_components:
        options.append(f'<option value="{component}">{component}</option>')
    return '\n'.join(options)


def prepare_report_data(stats, versions: List[str], custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    レポート生成に必要なデータを準備

    Args:
        stats: IssueStatistics オブジェクト
        versions: 分析対象のJDKバージョンリスト
        custom_config: カスタム設定

    Returns:
        テンプレートに渡すデータの辞書
    """
    config = custom_config or {}

    # 統計データの準備
    priority_stats = stats.get_priority_stats()
    component_stats = stats.get_component_stats()
    type_stats = stats.get_type_stats()
    os_stats = stats.get_os_stats()

    high_priority_count = stats.get_high_priority_count(['P1', 'P2'])
    windows_count = stats.get_windows_related_count()
    security_count = stats.get_security_related_count()

    # Issue一覧をJSON形式で準備
    issues_data = []
    for issue in stats.issues:
        issues_data.append({
            'id': issue.issue_id,
            'title': issue.title,
            'priority': issue.priority,
            'type': issue.type,
            'component': issue.component,
            'os': issue.os or '',
            'description': issue.description[:200] + '...' if len(issue.description) > 200 else issue.description
        })

    # レポートタイトルとサマリー
    title = config.get('title', f'JDK Issue Analysis Report - {", ".join(versions)}')
    summary = config.get('summary', 'JDKバージョン間のIssue分析レポート')

    # テンプレートデータの準備
    return {
        'title': title,
        'summary': summary,
        'versions_text': ', '.join(versions),
        'total_issues': len(stats.issues),
        'high_priority_count': high_priority_count,
        'windows_count': windows_count,
        'security_count': security_count,
        'issues_data': json.dumps(issues_data, ensure_ascii=False),
        'priority_stats': json.dumps(priority_stats),
        'component_stats': json.dumps(component_stats),
        'type_stats': json.dumps(type_stats),
        'os_stats': json.dumps(os_stats),
        'type_options': generate_type_options(type_stats),
        'component_options': generate_component_options(component_stats)
    }


# 使用例
if __name__ == '__main__':
    print("HTMLGenerator モジュール")
    print(f"Jinja2サポート: {'有効' if JINJA2_AVAILABLE else '無効（pip install jinja2を推奨）'}")
    print("\n使用方法:")
    print("  from html_generator import HTMLGenerator, prepare_report_data")
    print("  generator = HTMLGenerator()")
    print("  data = prepare_report_data(stats, versions)")
    print("  generator.generate(data, 'output.html')")
