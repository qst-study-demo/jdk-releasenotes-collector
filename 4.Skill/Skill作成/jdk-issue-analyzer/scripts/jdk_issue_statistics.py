#!/usr/bin/env python3
"""
JDK Issue Statistics Module

このモジュールは、JDK issueデータファイルから統計情報を抽出し、
フィルタリング、検索、分析の機能を提供します。
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from collections import defaultdict


@dataclass
class Issue:
    """単一のIssueを表すデータクラス"""
    issue_id: str
    title: str
    priority: str
    type: str
    component: str
    description: str
    os: Optional[str] = None

    def matches_filters(self, **filters) -> bool:
        """指定されたフィルタ条件に合致するかチェック"""
        for key, value in filters.items():
            if value is None:
                continue
            attr_value = getattr(self, key, None)
            if attr_value is None:
                return False
            if attr_value.lower() != value.lower():
                return False
        return True

    def contains_keyword(self, keyword: str, fields: List[str] = None) -> bool:
        """指定されたフィールドにキーワードが含まれるかチェック"""
        if fields is None:
            fields = ['title', 'description', 'component']
        
        keyword_lower = keyword.lower()
        for field in fields:
            value = getattr(self, field, None)
            if value and keyword_lower in value.lower():
                return True
        return False


class IssueStatistics:
    """Issue統計情報を管理するクラス"""
    
    def __init__(self, issues: List[Issue]):
        self.issues = issues
    
    def get_priority_stats(self) -> Dict[str, int]:
        """優先度別の統計を取得"""
        stats = defaultdict(int)
        for issue in self.issues:
            stats[issue.priority] += 1
        return dict(stats)
    
    def get_component_stats(self) -> Dict[str, int]:
        """コンポーネント別の統計を取得"""
        stats = defaultdict(int)
        for issue in self.issues:
            stats[issue.component] += 1
        return dict(stats)
    
    def get_type_stats(self) -> Dict[str, int]:
        """タイプ別の統計を取得"""
        stats = defaultdict(int)
        for issue in self.issues:
            stats[issue.type] += 1
        return dict(stats)
    
    def get_os_stats(self) -> Dict[str, int]:
        """OS別の統計を取得"""
        stats = defaultdict(int)
        for issue in self.issues:
            os = issue.os if issue.os else 'unknown'
            stats[os] += 1
        return dict(stats)
    
    def filter_issues(self, **filters) -> List[Issue]:
        """指定された条件でIssueをフィルタリング"""
        return [issue for issue in self.issues if issue.matches_filters(**filters)]
    
    def find_by_id(self, issue_id: str) -> Optional[Issue]:
        """Issue IDでIssueを検索（JDK-プレフィックスあり/なし両対応）"""
        # JDK-プレフィックスを正規化
        if not issue_id.upper().startswith('JDK-'):
            issue_id = f'JDK-{issue_id}'
        
        issue_id_upper = issue_id.upper()
        for issue in self.issues:
            if issue.issue_id.upper() == issue_id_upper:
                return issue
        return None
    
    def search_in_fields(self, keyword: str, fields: List[str] = None) -> List[Issue]:
        """指定されたフィールドでキーワード検索"""
        return [issue for issue in self.issues if issue.contains_keyword(keyword, fields)]
    
    def get_high_priority_count(self, priorities: List[str] = None) -> int:
        """高優先度Issueの数を取得"""
        if priorities is None:
            priorities = ['P1', 'P2']
        return len([i for i in self.issues if i.priority in priorities])
    
    def get_windows_related_count(self) -> int:
        """Windows関連Issueの数を取得"""
        return len([i for i in self.issues if i.os and 'windows' in i.os.lower()])
    
    def get_security_related_count(self) -> int:
        """セキュリティ関連Issueの数を取得"""
        return len([i for i in self.issues 
                   if 'security' in i.component.lower() or 
                   (i.description and 'security' in i.description.lower())])


def parse_issue_file(filepath: str) -> List[Issue]:
    """Issueファイルをパースして Issue オブジェクトのリストを返す"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ファイルを "-----" で分割
    blocks = content.split('\n-----\n')
    
    for block in blocks:
        if not block.strip():
            continue
        
        issue_data = {}
        lines = block.strip().split('\n')
        current_field = None
        current_value = []
        
        for line in lines:
            if line.startswith('Title: '):
                if current_field:
                    issue_data[current_field] = '\n'.join(current_value)
                current_field = 'title'
                current_value = [line[7:]]
            elif line.startswith('Priority: '):
                if current_field:
                    issue_data[current_field] = '\n'.join(current_value)
                current_field = 'priority'
                current_value = [line[10:]]
            elif line.startswith('Type: '):
                if current_field:
                    issue_data[current_field] = '\n'.join(current_value)
                current_field = 'type'
                current_value = [line[6:]]
            elif line.startswith('Component: '):
                if current_field:
                    issue_data[current_field] = '\n'.join(current_value)
                current_field = 'component'
                current_value = [line[11:]]
            elif line.startswith('Description: '):
                if current_field:
                    issue_data[current_field] = '\n'.join(current_value)
                current_field = 'description'
                current_value = [line[13:]]
            elif line.startswith('OS: '):
                if current_field:
                    issue_data[current_field] = '\n'.join(current_value)
                current_field = 'os'
                current_value = [line[4:]]
            else:
                if current_field:
                    current_value.append(line)
        
        # 最後のフィールドを保存
        if current_field:
            issue_data[current_field] = '\n'.join(current_value)
        
        # Issue IDを抽出
        if 'title' in issue_data:
            title = issue_data['title']
            if title.startswith('[') and ']' in title:
                issue_id = title[1:title.index(']')]
                issue_title = title[title.index(']') + 1:].strip()
                
                issue = Issue(
                    issue_id=issue_id,
                    title=issue_title,
                    priority=issue_data.get('priority', ''),
                    type=issue_data.get('type', ''),
                    component=issue_data.get('component', ''),
                    description=issue_data.get('description', ''),
                    os=issue_data.get('os')
                )
                issues.append(issue)
    
    return issues


def load_and_analyze(filepath: str) -> IssueStatistics:
    """Issueファイルを読み込み、統計オブジェクトを返す"""
    issues = parse_issue_file(filepath)
    return IssueStatistics(issues)


def load_multiple_files(filepaths: List[str]) -> IssueStatistics:
    """複数のIssueファイルを読み込み、統合した統計オブジェクトを返す"""
    all_issues = []
    for filepath in filepaths:
        issues = parse_issue_file(filepath)
        all_issues.extend(issues)
    return IssueStatistics(all_issues)
