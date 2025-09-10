"""
NGA论坛分析结果可视化脚本 - 修复中文字体版本
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
    plt.yticks(range(len(keywords)), keywords, fontproperties=chinese_font)
    plt.xlabel('出现次数', fontsize=12, fontweight='bold', fontproperties=chinese_font)
    plt.title(f'热门关键词TOP{top_n}', fontsize=16, fontweight='bold', pad=20, 
              fontproperties=chinese_font)
    
    # 在条形图上显示数值
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/keyword_frequency.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return keyword_counts

def main():
    """主函数"""
    # 查找最新的分类结果文件
    output_dir = './test_output'
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
    
    # 生成图表（测试版，只生成两个）
    categories = create_category_pie_chart(data, charts_dir)
    keywords = create_keyword_bar_chart(data, charts_dir)
    
    print(f"\n✅ 测试图表已生成完毕，保存在: {charts_dir}/")
    print("生成的图表包括:")
    print("- category_distribution.png (分类分布饼图)")
    print("- keyword_frequency.png (关键词频率条形图)")

if __name__ == "__main__":
    main()
