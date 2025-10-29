#!/usr/bin/env python3
"""
JDK Issue HTMLレポート生成スクリプト

複数のJDKバージョンのIssueデータを分析し、インタラクティブなHTMLレポートを生成します。
"""

import json
import sys
from typing import List, Dict, Any
from jdk_issue_statistics import load_multiple_files, IssueStatistics


def generate_html_report(stats: IssueStatistics, 
                        versions: List[str],
                        output_file: str = 'jdk_issue_report.html',
                        custom_config: Dict[str, Any] = None) -> None:
    """
    インタラクティブなHTMLレポートを生成
    
    Args:
        stats: IssueStatistics オブジェクト
        versions: 分析対象のJDKバージョンリスト
        output_file: 出力ファイル名
        custom_config: カスタム設定（タイトル、説明、表示項目など）
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
    
    html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }}
        
        header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .versions {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            margin-top: 20px;
            border-radius: 10px;
            font-size: 1.1em;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }}
        
        .card-title {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .card-value {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .card.priority {{ color: #dc3545; }}
        .card.priority .card-value {{ color: #dc3545; }}
        .card.windows {{ color: #0078d4; }}
        .card.windows .card-value {{ color: #0078d4; }}
        .card.security {{ color: #fd7e14; }}
        .card.security .card-value {{ color: #fd7e14; }}
        
        .charts-section {{
            padding: 40px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        
        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .chart-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .table-section {{
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .table-controls {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        
        .table-controls input,
        .table-controls select {{
            padding: 10px 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }}
        
        .table-controls input:focus,
        .table-controls select:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .table-controls input {{
            flex: 1;
            min-width: 300px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
            position: relative;
        }}
        
        th:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        th::after {{
            content: ' ↕';
            opacity: 0.5;
            font-size: 0.8em;
        }}
        
        th.sort-asc::after {{
            content: ' ↑';
            opacity: 1;
        }}
        
        th.sort-desc::after {{
            content: ' ↓';
            opacity: 1;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        
        tbody tr:hover {{
            background: #f8f9fa;
        }}
        
        .priority-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .priority-P1 {{ background: #dc3545; color: white; }}
        .priority-P2 {{ background: #fd7e14; color: white; }}
        .priority-P3 {{ background: #ffc107; color: black; }}
        .priority-P4 {{ background: #28a745; color: white; }}
        .priority-P5 {{ background: #6c757d; color: white; }}
        
        .type-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            background: #e9ecef;
            color: #495057;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            background: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 {title}</h1>
            <p>{summary}</p>
            <div class="versions">
                <strong>分析対象バージョン:</strong> {", ".join(versions)}
            </div>
        </header>
        
        <div class="summary-cards">
            <div class="card">
                <div class="card-title">総Issue数</div>
                <div class="card-value">{len(stats.issues)}</div>
            </div>
            <div class="card priority">
                <div class="card-title">高優先度 (P1-P2)</div>
                <div class="card-value">{high_priority_count}</div>
            </div>
            <div class="card windows">
                <div class="card-title">Windows関連</div>
                <div class="card-value">{windows_count}</div>
            </div>
            <div class="card security">
                <div class="card-title">セキュリティ関連</div>
                <div class="card-value">{security_count}</div>
            </div>
        </div>
        
        <div class="charts-section">
            <h2 style="font-size: 2em; margin-bottom: 10px;">📈 ビジュアル分析</h2>
            <div class="charts-grid">
                <div class="chart-container">
                    <div class="chart-title">優先度別分布</div>
                    <canvas id="priorityChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">コンポーネント別分布 (Top 10)</div>
                    <canvas id="componentChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">タイプ別分布</div>
                    <canvas id="typeChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">OS別分布</div>
                    <canvas id="osChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="table-section">
            <h2 style="font-size: 2em; margin-bottom: 20px;">📋 Issue一覧</h2>
            <div class="table-controls">
                <input type="text" id="searchInput" placeholder="🔍 Issueを検索...">
                <select id="priorityFilter">
                    <option value="">すべての優先度</option>
                    <option value="P1">P1</option>
                    <option value="P2">P2</option>
                    <option value="P3">P3</option>
                    <option value="P4">P4</option>
                    <option value="P5">P5</option>
                </select>
                <select id="typeFilter">
                    <option value="">すべてのタイプ</option>
                    {generate_type_options(type_stats)}
                </select>
                <select id="componentFilter">
                    <option value="">すべてのコンポーネント</option>
                    {generate_component_options(component_stats)}
                </select>
            </div>
            <table id="issuesTable">
                <thead>
                    <tr>
                        <th data-sort="id">Issue ID</th>
                        <th data-sort="priority">優先度</th>
                        <th data-sort="type">タイプ</th>
                        <th data-sort="component">コンポーネント</th>
                        <th data-sort="title">タイトル</th>
                        <th data-sort="os">OS</th>
                    </tr>
                </thead>
                <tbody id="issuesTableBody">
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Generated by JDK Issue Analyzer | {len(stats.issues)} issues analyzed</p>
        </footer>
    </div>
    
    <script>
        // データ
        const issuesData = {json.dumps(issues_data, ensure_ascii=False)};
        const priorityStats = {json.dumps(priority_stats)};
        const componentStats = {json.dumps(component_stats)};
        const typeStats = {json.dumps(type_stats)};
        const osStats = {json.dumps(os_stats)};
        
        // グラフの色設定
        const chartColors = [
            '#667eea', '#764ba2', '#f093fb', '#4facfe',
            '#43e97b', '#fa709a', '#fee140', '#30cfd0',
            '#a8edea', '#fed6e3', '#c471f5', '#fa8231'
        ];
        
        // 優先度チャート
        new Chart(document.getElementById('priorityChart'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(priorityStats),
                datasets: [{{
                    label: 'Issue数',
                    data: Object.values(priorityStats),
                    backgroundColor: chartColors[0],
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});
        
        // コンポーネントチャート (Top 10)
        const topComponents = Object.entries(componentStats)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);
        
        new Chart(document.getElementById('componentChart'), {{
            type: 'doughnut',
            data: {{
                labels: topComponents.map(c => c[0]),
                datasets: [{{
                    data: topComponents.map(c => c[1]),
                    backgroundColor: chartColors
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{ position: 'right' }}
                }}
            }}
        }});
        
        // タイプチャート
        new Chart(document.getElementById('typeChart'), {{
            type: 'pie',
            data: {{
                labels: Object.keys(typeStats),
                datasets: [{{
                    data: Object.values(typeStats),
                    backgroundColor: chartColors
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{ position: 'right' }}
                }}
            }}
        }});
        
        // OSチャート
        new Chart(document.getElementById('osChart'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(osStats),
                datasets: [{{
                    label: 'Issue数',
                    data: Object.values(osStats),
                    backgroundColor: chartColors[1],
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{ legend: {{ display: false }} }},
                indexAxis: 'y'
            }}
        }});
        
        // テーブル機能
        let currentSort = {{ column: 'priority', direction: 'asc' }};
        let filteredData = [...issuesData];
        
        function renderTable() {{
            const tbody = document.getElementById('issuesTableBody');
            tbody.innerHTML = '';
            
            filteredData.forEach(issue => {{
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${{issue.id}}</td>
                    <td><span class="priority-badge priority-${{issue.priority}}">${{issue.priority}}</span></td>
                    <td><span class="type-badge">${{issue.type}}</span></td>
                    <td>${{issue.component}}</td>
                    <td>${{issue.title}}</td>
                    <td>${{issue.os || '-'}}</td>
                `;
            }});
        }}
        
        function sortData(column) {{
            if (currentSort.column === column) {{
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            }} else {{
                currentSort.column = column;
                currentSort.direction = 'asc';
            }}
            
            filteredData.sort((a, b) => {{
                let aVal = a[column] || '';
                let bVal = b[column] || '';
                
                if (column === 'priority') {{
                    const priorityOrder = {{ 'P1': 1, 'P2': 2, 'P3': 3, 'P4': 4, 'P5': 5 }};
                    aVal = priorityOrder[aVal] || 99;
                    bVal = priorityOrder[bVal] || 99;
                }}
                
                if (aVal < bVal) return currentSort.direction === 'asc' ? -1 : 1;
                if (aVal > bVal) return currentSort.direction === 'asc' ? 1 : -1;
                return 0;
            }});
            
            // ソート状態を表示
            document.querySelectorAll('th').forEach(th => {{
                th.classList.remove('sort-asc', 'sort-desc');
            }});
            document.querySelector(`th[data-sort="${{column}}"]`)
                .classList.add(`sort-${{currentSort.direction}}`);
            
            renderTable();
        }}
        
        function filterData() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const priorityFilter = document.getElementById('priorityFilter').value;
            const typeFilter = document.getElementById('typeFilter').value;
            const componentFilter = document.getElementById('componentFilter').value;
            
            filteredData = issuesData.filter(issue => {{
                const matchesSearch = !searchTerm || 
                    issue.title.toLowerCase().includes(searchTerm) ||
                    issue.id.toLowerCase().includes(searchTerm) ||
                    issue.description.toLowerCase().includes(searchTerm);
                const matchesPriority = !priorityFilter || issue.priority === priorityFilter;
                const matchesType = !typeFilter || issue.type === typeFilter;
                const matchesComponent = !componentFilter || issue.component === componentFilter;
                
                return matchesSearch && matchesPriority && matchesType && matchesComponent;
            }});
            
            renderTable();
        }}
        
        // イベントリスナー
        document.querySelectorAll('th[data-sort]').forEach(th => {{
            th.addEventListener('click', () => sortData(th.dataset.sort));
        }});
        
        document.getElementById('searchInput').addEventListener('input', filterData);
        document.getElementById('priorityFilter').addEventListener('change', filterData);
        document.getElementById('typeFilter').addEventListener('change', filterData);
        document.getElementById('componentFilter').addEventListener('change', filterData);
        
        // 初期表示
        renderTable();
    </script>
</body>
</html>'''
    
    # ファイルに書き込み
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ レポートを生成しました: {output_file}")


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
