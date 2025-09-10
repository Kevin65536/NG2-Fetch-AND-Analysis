"""
NGA Cookies设置工具

由于NGA论坛需要登录才能访问用户主题列表，这个工具帮助你设置从浏览器获取的cookies。

使用步骤：
1. 在浏览器中登录NGA论坛 (ngabbs.com)
2. 访问任意用户的主题列表页面（确保能正常显示）
3. 从浏览器开发者工具中获取cookies
4. 运行此脚本设置cookies

如何获取cookies：
1. 在浏览器中按F12打开开发者工具
2. 切换到"Network"(网络)标签页
3. 刷新页面
4. 找到第一个请求，在请求头中找到"Cookie"字段
5. 复制Cookie值
"""

import json
import sys
import os

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nga_fetcher import NGAFetcher

def parse_cookie_string(cookie_string: str) -> dict:
    """解析cookie字符串为字典格式"""
    cookies_dict = {}
    
    if not cookie_string:
        return cookies_dict
    
    # 分割cookie字符串
    pairs = cookie_string.split(';')
    
    for pair in pairs:
        pair = pair.strip()
        if '=' in pair:
            key, value = pair.split('=', 1)
            cookies_dict[key.strip()] = value.strip()
    
    return cookies_dict

def set_cookies_interactive():
    """交互式设置cookies"""
    print("NGA Cookies 设置工具")
    print("=" * 50)
    
    print("\n请按照以下步骤操作：")
    print("1. 在浏览器中登录 ngabbs.com")
    print("2. 访问用户主题列表页面")
    print("3. 从开发者工具中复制Cookie值")
    print("4. 粘贴到下面的输入框中")
    
    print("\n如何获取Cookie值：")
    print("- 按F12打开开发者工具")
    print("- 点击Network(网络)标签")
    print("- 刷新页面")
    print("- 点击第一个请求")
    print("- 在Request Headers中找到Cookie字段")
    print("- 复制Cookie的值（不包括'Cookie: '前缀）")
    
    print("\n" + "-" * 50)
    cookie_string = input("请粘贴Cookie值: ").strip()
    
    if not cookie_string:
        print("未输入Cookie值，退出。")
        return
    
    # 解析cookies
    cookies_dict = parse_cookie_string(cookie_string)
    
    if not cookies_dict:
        print("Cookie解析失败，请检查输入。")
        return
    
    print(f"\n解析到 {len(cookies_dict)} 个cookie项:")
    for key in list(cookies_dict.keys())[:5]:  # 只显示前5个
        value = cookies_dict[key]
        display_value = value[:20] + "..." if len(value) > 20 else value
        print(f"  {key} = {display_value}")
    
    if len(cookies_dict) > 5:
        print(f"  ... 还有 {len(cookies_dict) - 5} 个")
    
    # 测试cookies
    print("\n正在测试cookies有效性...")
    
    try:
        fetcher = NGAFetcher()
        if fetcher.set_cookies_from_browser(cookies_dict):
            print("✅ Cookies设置成功！")
            print("现在可以使用爬虫进行用户主题爬取了。")
            
            # 简单测试
            test = input("\n是否测试获取用户主题列表？(y/N): ").strip().lower()
            if test in ['y', 'yes']:
                user_id = input("请输入要测试的用户ID (默认: 24278093): ").strip() or "24278093"
                print(f"\n正在测试获取用户 {user_id} 的主题列表...")
                
                topics = fetcher.fetch_user_topics(user_id, max_pages=1)
                if topics:
                    print(f"✅ 成功获取到 {len(topics)} 个主题!")
                    for i, topic in enumerate(topics[:3], 1):
                        print(f"  {i}. {topic['title']}")
                else:
                    print("❌ 未获取到主题")
        else:
            print("❌ Cookies无效或设置失败")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

def set_cookies_from_file():
    """从文件设置cookies"""
    cookie_file = "cookies.txt"
    
    if not os.path.exists(cookie_file):
        print(f"cookies文件 {cookie_file} 不存在")
        print("请创建该文件并将Cookie字符串放入其中")
        return
    
    try:
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookie_string = f.read().strip()
        
        cookies_dict = parse_cookie_string(cookie_string)
        
        fetcher = NGAFetcher()
        if fetcher.set_cookies_from_browser(cookies_dict):
            print("✅ 从文件设置Cookies成功！")
        else:
            print("❌ Cookies无效")
            
    except Exception as e:
        print(f"❌ 从文件设置cookies失败: {e}")

def main():
    print("请选择设置方式：")
    print("1. 交互式输入Cookie")
    print("2. 从cookies.txt文件读取")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        set_cookies_interactive()
    elif choice == "2":
        set_cookies_from_file()
    else:
        print("无效选择")

if __name__ == "__main__":
    main()
