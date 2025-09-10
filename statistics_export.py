"""
NGA论坛分析结果详细统计表格导出工具
"""

import json
import pandas as pd
import os
from collections import Counter
from datetime import datetime
import argparse


def load_classification_data(json_file):
    """加载分类数据"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def export_category_statistics(data, output_dir="./statistics"):
    """导出分类统计表格"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 统计分类分布
    categories = {}
    for post in data['posts']:
        category = post['classification']['categories'][0] if post['classification']['categories'] else '未分类'
        categories[category] = categories.get(category, 0) + 1
    
    # 创建DataFrame
    total_posts = sum(categories.values())
    category_data = []
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_posts) * 100
        category_data.append({
            '分类': category,
            '帖子数量': count,
            '百分比': f"{percentage:.2f}%",
            '数值百分比': percentage
        })
    
    df_categories = pd.DataFrame(category_data)
    
    # 保存为多种格式
    df_categories.to_csv(f'{output_dir}/category_statistics.csv', index=False, encoding='utf-8-sig')
    df_categories.to_excel(f'{output_dir}/category_statistics.xlsx', index=False, engine='openpyxl')
    
    print(f"分类统计表格已保存到: {output_dir}/category_statistics.csv 和 .xlsx")
    return df_categories


def export_keyword_statistics(data, output_dir="./statistics", min_count=1):
    """导出关键词统计表格（完整列表）"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 统计所有关键词
    all_keywords = []
    for post in data['posts']:
        keywords = post['classification'].get('keywords', [])
        all_keywords.extend(keywords)
    
    keyword_counts = Counter(all_keywords)
    
    # 创建完整关键词统计表
    keyword_data = []
    total_keyword_mentions = sum(keyword_counts.values())
    
    for keyword, count in keyword_counts.most_common():
        if count >= min_count:  # 过滤掉出现次数太少的关键词
            percentage = (count / total_keyword_mentions) * 100
            keyword_data.append({
                '关键词': keyword,
                '出现次数': count,
                '百分比': f"{percentage:.2f}%",
                '数值百分比': percentage
            })
    
    df_keywords = pd.DataFrame(keyword_data)
    
    # 保存完整关键词列表
    df_keywords.to_csv(f'{output_dir}/keyword_statistics_full.csv', index=False, encoding='utf-8-sig')
    df_keywords.to_excel(f'{output_dir}/keyword_statistics_full.xlsx', index=False, engine='openpyxl')
    
    # 创建TOP关键词表格（多个不同的TOP数量）
    for top_n in [10, 20, 50, 100]:
        if len(df_keywords) >= top_n:
            top_df = df_keywords.head(top_n)
            top_df.to_csv(f'{output_dir}/keyword_statistics_top{top_n}.csv', index=False, encoding='utf-8-sig')
            top_df.to_excel(f'{output_dir}/keyword_statistics_top{top_n}.xlsx', index=False, engine='openpyxl')
    
    print(f"关键词统计表格已保存到: {output_dir}/keyword_statistics_*.csv 和 .xlsx")
    print(f"总关键词数量: {len(keyword_data)} (出现次数>={min_count})")
    return df_keywords


def export_author_statistics(data, output_dir="./statistics", min_posts=1):
    """导出作者活跃度统计表格"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 统计作者发帖数
    author_counts = Counter()
    for post in data['posts']:
        author = post.get('author', '未知用户')
        author_counts[author] += 1
    
    # 创建作者统计表
    author_data = []
    total_posts = sum(author_counts.values())
    
    for author, count in author_counts.most_common():
        if count >= min_posts:
            percentage = (count / total_posts) * 100
            author_data.append({
                '作者': author,
                '发帖数量': count,
                '百分比': f"{percentage:.2f}%",
                '数值百分比': percentage
            })
    
    df_authors = pd.DataFrame(author_data)
    
    # 保存表格
    df_authors.to_csv(f'{output_dir}/author_statistics.csv', index=False, encoding='utf-8-sig')
    df_authors.to_excel(f'{output_dir}/author_statistics.xlsx', index=False, engine='openpyxl')
    
    print(f"作者统计表格已保存到: {output_dir}/author_statistics.csv 和 .xlsx")
    print(f"活跃作者数量: {len(author_data)} (发帖数>={min_posts})")
    return df_authors


def export_confidence_statistics(data, output_dir="./statistics"):
    """导出置信度统计表格"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 收集置信度数据
    confidence_data = []
    for i, post in enumerate(data['posts'], 1):
        confidence = post['classification'].get('confidence', 0)
        category = post['classification']['categories'][0] if post['classification']['categories'] else '未分类'
        keywords = ', '.join(post['classification'].get('keywords', [])[:5])  # 前5个关键词
        
        confidence_data.append({
            '序号': i,
            '帖子标题': post.get('title', '无标题')[:50] + ('...' if len(post.get('title', '')) > 50 else ''),
            '分类': category,
            '置信度': confidence,
            '关键词': keywords,
            '作者': post.get('author', '未知')
        })
    
    df_confidence = pd.DataFrame(confidence_data)
    
    # 按置信度排序
    df_confidence_sorted = df_confidence.sort_values('置信度', ascending=False)
    
    # 保存表格
    df_confidence_sorted.to_csv(f'{output_dir}/confidence_statistics.csv', index=False, encoding='utf-8-sig')
    df_confidence_sorted.to_excel(f'{output_dir}/confidence_statistics.xlsx', index=False, engine='openpyxl')
    
    # 创建置信度分布统计
    confidence_ranges = [
        (0.9, 1.0, '高置信度 (0.9-1.0)'),
        (0.7, 0.9, '中高置信度 (0.7-0.9)'),
        (0.5, 0.7, '中等置信度 (0.5-0.7)'),
        (0.3, 0.5, '中低置信度 (0.3-0.5)'),
        (0.0, 0.3, '低置信度 (0.0-0.3)')
    ]
    
    range_data = []
    total_posts = len(df_confidence)
    
    for min_conf, max_conf, label in confidence_ranges:
        count = len(df_confidence[(df_confidence['置信度'] >= min_conf) & (df_confidence['置信度'] < max_conf)])
        if min_conf == 0.9:  # 最高范围包含1.0
            count = len(df_confidence[df_confidence['置信度'] >= min_conf])
        
        percentage = (count / total_posts) * 100
        range_data.append({
            '置信度范围': label,
            '帖子数量': count,
            '百分比': f"{percentage:.2f}%",
            '数值百分比': percentage
        })
    
    df_ranges = pd.DataFrame(range_data)
    df_ranges.to_csv(f'{output_dir}/confidence_distribution.csv', index=False, encoding='utf-8-sig')
    df_ranges.to_excel(f'{output_dir}/confidence_distribution.xlsx', index=False, engine='openpyxl')
    
    print(f"置信度统计表格已保存到: {output_dir}/confidence_statistics.csv 和 .xlsx")
    print(f"置信度分布已保存到: {output_dir}/confidence_distribution.csv 和 .xlsx")
    return df_confidence_sorted, df_ranges


def export_category_keyword_matrix(data, output_dir="./statistics", top_keywords=20):
    """导出分类-关键词关联矩阵表格"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 统计每个分类的关键词
    category_keywords = {}
    for post in data['posts']:
        category = post['classification']['categories'][0] if post['classification']['categories'] else '未分类'
        keywords = post['classification'].get('keywords', [])
        
        if category not in category_keywords:
            category_keywords[category] = Counter()
        
        for keyword in keywords:
            category_keywords[category][keyword] += 1
    
    # 获取最常见的关键词
    all_keywords = Counter()
    for counter in category_keywords.values():
        all_keywords.update(counter)
    
    top_keywords_list = [kw for kw, _ in all_keywords.most_common(top_keywords)]
    categories = list(category_keywords.keys())
    
    # 创建矩阵数据
    matrix_data = []
    for category in categories:
        row_data = {'分类': category}
        for keyword in top_keywords_list:
            count = category_keywords[category].get(keyword, 0)
            row_data[keyword] = count
        matrix_data.append(row_data)
    
    df_matrix = pd.DataFrame(matrix_data)
    
    # 保存矩阵表格
    df_matrix.to_csv(f'{output_dir}/category_keyword_matrix.csv', index=False, encoding='utf-8-sig')
    df_matrix.to_excel(f'{output_dir}/category_keyword_matrix.xlsx', index=False, engine='openpyxl')
    
    print(f"分类-关键词矩阵已保存到: {output_dir}/category_keyword_matrix.csv 和 .xlsx")
    return df_matrix


def create_summary_report(output_dir="./statistics"):
    """创建汇总报告"""
    os.makedirs(output_dir, exist_ok=True)
    
    report = f"""
# NGA二次元国家地理版块详细统计报告

## 生成时间
{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

## 导出的统计表格文件

### 1. 分类统计
- `category_statistics.csv/.xlsx` - 版块内容分类分布统计

### 2. 关键词统计
- `keyword_statistics_full.csv/.xlsx` - 完整关键词列表
- `keyword_statistics_top10.csv/.xlsx` - TOP10热门关键词
- `keyword_statistics_top20.csv/.xlsx` - TOP20热门关键词  
- `keyword_statistics_top50.csv/.xlsx` - TOP50热门关键词
- `keyword_statistics_top100.csv/.xlsx` - TOP100热门关键词

### 3. 作者活跃度统计
- `author_statistics.csv/.xlsx` - 作者发帖数量统计

### 4. 置信度分析
- `confidence_statistics.csv/.xlsx` - 每个帖子的详细置信度信息
- `confidence_distribution.csv/.xlsx` - 置信度分布统计

### 5. 关联分析
- `category_keyword_matrix.csv/.xlsx` - 分类与关键词关联矩阵

## 文件说明
- `.csv` 文件：适合用Excel打开，兼容性好
- `.xlsx` 文件：Excel原生格式，支持更多功能
- 所有文件均使用UTF-8编码，确保中文正确显示

## 使用建议
1. 使用Excel打开.xlsx文件进行数据分析
2. 可以基于这些表格创建透视表和图表
3. 关键词统计表可用于词云生成
4. 置信度数据可用于模型性能评估

---
报告生成于: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
"""
    
    with open(f'{output_dir}/统计报告说明.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"统计报告说明已保存到: {output_dir}/统计报告说明.md")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='NGA论坛分析结果详细统计表格导出工具')
    parser.add_argument('-i', '--input', required=True, help='输入的JSON分类结果文件')
    parser.add_argument('-o', '--output', default='./statistics', help='输出目录 (默认: ./statistics)')
    parser.add_argument('--min-keyword-count', type=int, default=1, help='关键词最小出现次数 (默认: 1)')
    parser.add_argument('--min-author-posts', type=int, default=1, help='作者最小发帖数 (默认: 1)')
    parser.add_argument('--top-keywords', type=int, default=20, help='关联矩阵中包含的热门关键词数量 (默认: 20)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"错误：输入文件 {args.input} 不存在")
        return
    
    print(f"正在处理文件: {args.input}")
    print(f"输出目录: {args.output}")
    
    # 加载数据
    data = load_classification_data(args.input)
    print(f"加载了 {len(data['posts'])} 个帖子的数据")
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    
    print("\n开始导出统计表格...")
    
    # 导出各种统计表格
    export_category_statistics(data, args.output)
    export_keyword_statistics(data, args.output, args.min_keyword_count)
    export_author_statistics(data, args.output, args.min_author_posts)
    export_confidence_statistics(data, args.output)
    export_category_keyword_matrix(data, args.output, args.top_keywords)
    
    # 创建汇总报告
    create_summary_report(args.output)
    
    print(f"\n✅ 所有统计表格已导出完毕！")
    print(f"📁 输出目录: {args.output}")
    print(f"📋 请查看 '{args.output}/统计报告说明.md' 了解各文件详情")


if __name__ == "__main__":
    # 如果没有命令行参数，尝试自动查找最新的分类结果文件
    import sys
    if len(sys.argv) == 1:
        print("未提供输入文件，尝试查找最新的分类结果...")
        
        # 查找最新的分类结果文件
        search_dirs = ['./test_output', './output', './production_output']
        json_files = []
        
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                files = [f for f in os.listdir(search_dir) if f.startswith('nga_classification_') and f.endswith('.json')]
                json_files.extend([os.path.join(search_dir, f) for f in files])
        
        if json_files:
            # 使用最新的文件
            latest_file = sorted(json_files, key=os.path.getmtime)[-1]
            print(f"找到最新文件: {latest_file}")
            
            # 自动运行
            data = load_classification_data(latest_file)
            print(f"加载了 {len(data['posts'])} 个帖子的数据")
            
            output_dir = "./statistics"
            os.makedirs(output_dir, exist_ok=True)
            
            print("\n开始导出统计表格...")
            export_category_statistics(data, output_dir)
            export_keyword_statistics(data, output_dir)
            export_author_statistics(data, output_dir)
            export_confidence_statistics(data, output_dir)
            export_category_keyword_matrix(data, output_dir)
            create_summary_report(output_dir)
            
            print(f"\n✅ 所有统计表格已导出完毕！")
            print(f"📁 输出目录: {output_dir}")
        else:
            print("未找到分类结果文件，请手动指定输入文件")
            print("使用方法: python statistics_export.py -i <输入文件>")
    else:
        main()
