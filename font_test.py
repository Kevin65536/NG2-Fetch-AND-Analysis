"""
测试中文字体显示的简单脚本
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 方法1：使用字体路径
def method1():
    print("=== 方法1：使用字体路径 ===")
    # Windows系统中文字体路径
    font_paths = [
        'C:\\Windows\\Fonts\\msyh.ttc',  # 微软雅黑
        'C:\\Windows\\Fonts\\simhei.ttf',  # 黑体
        'C:\\Windows\\Fonts\\simsun.ttc',  # 宋体
    ]
    
    for font_path in font_paths:
        try:
            import os
            if os.path.exists(font_path):
                print(f"找到字体文件: {font_path}")
                return font_path
        except Exception as e:
            continue
    return None

# 方法2：使用字体管理器
def method2():
    print("=== 方法2：使用字体管理器 ===")
    font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    for font in font_list:
        if 'yahei' in font.lower() or 'msyh' in font.lower():
            print(f"找到微软雅黑: {font}")
            return font
        elif 'simhei' in font.lower():
            print(f"找到黑体: {font}")
            return font
    return None

# 测试
font_path = method1()
if not font_path:
    font_path = method2()

if font_path:
    print(f"将使用字体: {font_path}")
    
    # 创建测试图表
    plt.figure(figsize=(8, 6))
    
    # 使用字体路径设置字体
    prop = fm.FontProperties(fname=font_path)
    
    plt.text(0.5, 0.5, '测试中文显示：二次元国家地理版块内容分类分布', 
             horizontalalignment='center',
             verticalalignment='center',
             fontproperties=prop,
             fontsize=16)
    
    plt.title('中文字体测试', fontproperties=prop, fontsize=18)
    plt.xlabel('横轴标签', fontproperties=prop, fontsize=14)
    plt.ylabel('纵轴标签', fontproperties=prop, fontsize=14)
    
    plt.savefig('font_test.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("字体测试完成！")
else:
    print("未找到合适的中文字体！")
