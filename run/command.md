# issueを分類して集計
cd run/command.md
python extract_jdk.py
python fetch_jdk_issues.py
python aggregate_jdk_issues.py

# issueのtitle/summaryを1ファイルにまとめる
python merge_jdk_issues.py --content-mode summary