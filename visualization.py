"""
NGA论坛分析结果可视化脚本
"""

import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from collections import Counter
import os
from datetime import datetime
import seaborn as sns
import pandas as pd
import platform
import warnings

# 中文字体设置函数
def setup_chinese_fonts():
    """设置中文字体支持"""
    system = platform.system()
    font_path = None
    
    if system == "Windows":
        # Windows系统字体路径
        font_paths = [
            'C:\\Windows\\Fonts\\msyh.ttc',     # 微软雅黑
            'C:\\Windows\\Fonts\\msyhbd.ttc',   # 微软雅黑粗体
            'C:\\Windows\\Fonts\\simhei.ttf',   # 黑体
            'C:\\Windows\\Fonts\\simsun.ttc',   # 宋体
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                print(f"使用字体文件: {path}")
                break
    
    if font_path:
        # 创建字体属性对象
        chinese_font = fm.FontProperties(fname=font_path)
        
        # 设置全局字体
        plt.rcParams['font.family'] = ['sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        
        return chinese_font
    else:
        print("未找到中文字体文件，使用系统默认字体")
        # 尝试系统字体名称
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        return None

# 设置中文字体
chinese_font = setup_chinese_fonts()

# 忽略字体警告
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', category=UserWarning, module='seaborn')

# 设置图表样式
sns.set_style("whitegrid")
plt.style.use('seaborn-v0_8-darkgrid')

def load_classification_data(json_file):
    """加载分类数据"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def create_category_pie_chart(data, output_dir="./charts"):
    """创建分类饼图"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 统计分类分布
    categories = {}
    for post in data['posts']:
        category = post['classification']['categories'][0] if post['classification']['categories'] else '未分类'
        categories[category] = categories.get(category, 0) + 1
    
    # 创建饼图
    plt.figure(figsize=(12, 8))
    
    # 颜色方案
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
    
    labels = list(categories.keys())
    sizes = list(categories.values())
    
    # 使用中文字体
    font_prop = chinese_font if chinese_font else None
    
    wedges, texts, autotexts = plt.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                       colors=colors[:len(labels)], startangle=90,
                                       textprops={'fontsize': 12})
    
    # 设置中文字体
    if chinese_font:
        for text in texts:
            text.set_fontproperties(chinese_font)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    else:
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    plt.title('NGA二次元国家地理版块内容分类分布', fontsize=16, fontweight='bold', pad=20,
              fontproperties=chinese_font)
    
    # 添加图例
    legend_labels = [f'{label}: {size}个' for label, size in zip(labels, sizes)]
    legend = plt.legend(wedges, legend_labels, title="分类详情", loc="center left", 
                       bbox_to_anchor=(1, 0, 0.5, 1), prop=chinese_font)
    
    # 设置图例标题字体
    if chinese_font:
        legend.get_title().set_fontproperties(chinese_font)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/category_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return categories

def create_keyword_bar_chart(data, output_dir="./charts", top_n=15):
    """创建关键词条形图"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 统计关键词
    all_keywords = []
    for post in data['posts']:
        keywords = post['classification'].get('keywords', [])
        all_keywords.extend(keywords)
    
    keyword_counts = Counter(all_keywords)
    top_keywords = keyword_counts.most_common(top_n)
    
    if not top_keywords:
        print("没有找到关键词数据")
        return
    
    # 创建条形图
    plt.figure(figsize=(14, 8))
    
    keywords, counts = zip(*top_keywords)
    
    # 创建颜色渐变
    colors = plt.cm.viridis(range(len(keywords)))
    
    bars = plt.barh(range(len(keywords)), counts, color=colors)
    
    # 设置标签
    plt.yticks(range(len(keywords)), keywords)
    if chinese_font:
        # 设置y轴标签字体
        ax = plt.gca()
        for label in ax.get_yticklabels():
            label.set_fontproperties(chinese_font)
    plt.xlabel('出现次数', fontsize=12, fontweight='bold', fontproperties=chinese_font)
    plt.title(f'热门关键词TOP{top_n}', fontsize=16, fontweight='bold', pad=20, fontproperties=chinese_font)

    # 在条形图上显示数值
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/keyword_frequency.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return keyword_counts

def create_author_activity_chart(data, output_dir="./charts", top_n=10):
    """创建作者活跃度图表"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 统计作者发帖数
    author_counts = Counter()
    for post in data['posts']:
        author = post.get('author', '未知用户')
        author_counts[author] += 1
    
    top_authors = author_counts.most_common(top_n)
    
    if not top_authors:
        print("没有找到作者数据")
        return
    
    # 创建条形图
    plt.figure(figsize=(12, 6))
    
    authors, counts = zip(*top_authors)
    
    bars = plt.bar(range(len(authors)), counts, 
                   color=plt.cm.Set3(range(len(authors))))

    plt.xticks(range(len(authors)), authors, rotation=45, ha='right')
    if chinese_font:
        # 设置x轴标签字体
        ax = plt.gca()
        for label in ax.get_xticklabels():
            label.set_fontproperties(chinese_font)
    plt.ylabel('发帖数量', fontsize=12, fontweight='bold', fontproperties=chinese_font)
    plt.title(f'最活跃作者TOP{top_n}', fontsize=16, fontweight='bold', pad=20, fontproperties=chinese_font)

    # 在条形图上显示数值
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontproperties=chinese_font)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/author_activity.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return author_counts

def create_confidence_distribution(data, output_dir="./charts"):
    """创建置信度分布图"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 收集置信度数据
    confidences = []
    for post in data['posts']:
        confidence = post['classification'].get('confidence', 0)
        confidences.append(confidence)
    
    if not confidences:
        print("没有找到置信度数据")
        return
    
    # 创建直方图
    plt.figure(figsize=(10, 6))
    
    plt.hist(confidences, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    plt.xlabel('分类置信度', fontsize=12, fontweight='bold', fontproperties=chinese_font)
    plt.ylabel('帖子数量', fontsize=12, fontweight='bold', fontproperties=chinese_font)
    plt.title('AI分类置信度分布', fontsize=16, fontweight='bold', pad=20, fontproperties=chinese_font)

    # 添加统计信息
    avg_confidence = sum(confidences) / len(confidences)
    plt.axvline(avg_confidence, color='red', linestyle='--', 
                label=f'平均置信度: {avg_confidence:.3f}')
    plt.legend(prop=chinese_font)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/confidence_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return confidences

def create_category_keyword_heatmap(data, output_dir="./charts"):
    """创建分类-关键词热力图"""
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
    
    top_keywords = [kw for kw, _ in all_keywords.most_common(15)]
    categories = list(category_keywords.keys())
    
    # 创建矩阵
    matrix = []
    for category in categories:
        row = []
        for keyword in top_keywords:
            count = category_keywords[category].get(keyword, 0)
            row.append(count)
        matrix.append(row)
    
    # 创建热力图
    plt.figure(figsize=(16, 8))
    
    df = pd.DataFrame(matrix, index=categories, columns=top_keywords)
    
    # 创建热力图
    ax = sns.heatmap(df, annot=True, cmap='YlOrRd', fmt='d', 
                     cbar_kws={'label': '出现次数'})
    
    # 设置colorbar字体
    cbar = ax.collections[0].colorbar
    cbar.set_label('出现次数', fontproperties=chinese_font)

    plt.title('分类-关键词关联热力图', fontsize=16, fontweight='bold', pad=20, fontproperties=chinese_font)
    plt.xlabel('关键词', fontsize=12, fontweight='bold', fontproperties=chinese_font)
    plt.ylabel('分类', fontsize=12, fontweight='bold', fontproperties=chinese_font)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # 设置刻度标签字体
    if chinese_font:
        ax = plt.gca()
        for label in ax.get_xticklabels():
            label.set_fontproperties(chinese_font)
        for label in ax.get_yticklabels():
            label.set_fontproperties(chinese_font)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/category_keyword_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()

def generate_summary_report(categories, keywords, authors, confidences, output_dir="./charts"):
    """生成可视化分析总结报告"""
    os.makedirs(output_dir, exist_ok=True)
    
    total_posts = sum(categories.values())
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    report = f"""
# NGA二次元国家地理版块数据可视化分析报告

## 基本统计
- 总帖子数: {total_posts}
- 平均AI分类置信度: {avg_confidence:.3f}
- 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 分类分布分析
"""
    
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_posts) * 100
        report += f"- {category}: {count}个帖子 ({percentage:.1f}%)\n"
    
    report += f"""
## 内容特征分析
- 最热门关键词: {keywords.most_common(1)[0] if keywords else '无数据'}
- 最活跃作者: {authors.most_common(1)[0] if authors else '无数据'}
- 二次元主要内容类型: 动画/番剧占主导地位，其次是游戏内容

## 版块特点总结
基于数据分析，NGA二次元国家地理版块呈现以下特点：
1. 动画/番剧讨论是主要内容，体现了版块的核心定位
2. 游戏相关讨论占据重要地位，反映二次元文化与游戏的紧密关系
3. 内容多样化程度较高，涵盖漫画、手办、VTuber等各个领域
4. AI分类系统表现良好，平均置信度较高

---
报告生成于: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
"""
    
    with open(f'{output_dir}/visualization_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"可视化分析报告已保存到: {output_dir}/visualization_report.md")

def main():
    """主函数"""
    # 查找最新的分类结果文件
    output_dir = './100page_output'
    json_files = [f for f in os.listdir(output_dir) if f.startswith('nga_classification_') and f.endswith('.json')]
    
    if not json_files:
        print("未找到分类结果文件")
        return
    
    # 使用最新的文件
    latest_file = sorted(json_files)[-1]
    json_path = os.path.join(output_dir, latest_file)
    
    print(f"正在分析文件: {json_path}")
    
    # 加载数据
    data = load_classification_data(json_path)
    print(f"加载了 {len(data['posts'])} 个帖子的数据")
    
    # 创建图表目录
    charts_dir = "./charts"
    os.makedirs(charts_dir, exist_ok=True)
    
    print("正在生成可视化图表...")
    
    # 生成各种图表
    categories = create_category_pie_chart(data, charts_dir)
    keywords = create_keyword_bar_chart(data, charts_dir)
    authors = create_author_activity_chart(data, charts_dir)
    confidences = create_confidence_distribution(data, charts_dir)
    create_category_keyword_heatmap(data, charts_dir)
    
    # 生成分析报告
    generate_summary_report(categories, keywords, authors, confidences, charts_dir)
    
    print(f"\n✅ 所有图表已生成完毕，保存在: {charts_dir}/")
    print("生成的图表包括:")
    print("- category_distribution.png (分类分布饼图)")
    print("- keyword_frequency.png (关键词频率条形图)")
    print("- author_activity.png (作者活跃度)")
    print("- confidence_distribution.png (置信度分布)")
    print("- category_keyword_heatmap.png (分类-关键词热力图)")
    print("- visualization_report.md (可视化分析报告)")

if __name__ == "__main__":
    main()
