"""
NGA论坛帖子内容分类工具配置文件
"""

import os
from datetime import datetime, timedelta

# NGA论坛相关配置
NGA_BASE_URL = "https://ngabbs.com"
NGA_FORUM_URL = "https://ngabbs.com/thread.php"  # 版块URL
NGA_LOGIN_URL = "https://ngabbs.com/nuke.php?__lib=login&__act=login&login"

# 版块配置
TARGET_FORUM_ID = "-447601"  # 二次元国家地理版块ID
TARGET_FORUM_NAME = "二次元国家地理"

# 登录相关配置（需要用户手动填写）
# 注意：请不要在代码中直接填写密码，建议使用环境变量或配置文件
NGA_USERNAME = ""  # 用户名
NGA_PASSWORD = ""  # 密码
USE_COOKIES_FILE = True  # 是否使用cookies文件进行免登录
COOKIES_FILE = "nga_cookies.json"  # cookies文件路径

# 请求相关配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"'
}

# 页数配置
DEFAULT_MAX_PAGES = 10  # 默认最大页数
MAX_PAGES_LIMIT = 100  # 最大页数限制

# Ollama配置
OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama服务器地址
OLLAMA_MODEL = "gemma3:latest"  # 使用的模型名称（更改为可用模型）
OLLAMA_TIMEOUT = 60  # Ollama请求超时时间

# 分类配置
CLASSIFICATION_CATEGORIES = [
    "动画/番剧",
    "游戏",
    "漫画",
    "轻小说",
    "虚拟主播/VTuber", 
    "手办/周边",
    "音乐/歌曲",
    "其他"
]

# 分类提示词模板
CLASSIFICATION_PROMPT = """
请分析以下NGA论坛帖子的内容，判断其主要讨论的二次元内容类型。

帖子标题：{title}
帖子内容：{content}

请从以下分类中选择最合适的1个分类（只选择最主要的分类）：
1. 动画/番剧
2. 游戏  
3. 漫画
4. 轻小说
5. 虚拟主播/VTuber
6. 手办/周边
7. 音乐/歌曲
8. 其他

同时请尝试提取具体的作品名称、角色名或其他关键词。

请以JSON格式回复，包含以下字段：
- categories: 分类列表
- keywords: 关键词列表
- confidence: 置信度(0-1)

示例格式：
{{"categories": ["动画/番剧"], "keywords": ["某某动画", "某某角色"], "confidence": 0.9}}
"""

# 请求配置
REQUEST_DELAY = 1  # 请求间隔（秒）
TIMEOUT = 30  # 请求超时时间
RETRY_TIMES = 3  # 重试次数

# 内容解析配置
MAX_CONTENT_LENGTH = 5000  # 最大内容长度（字符）
EXTRACT_REPLIES = False  # 是否提取回复内容（暂时只分析楼主内容）

# 输出配置
DEFAULT_OUTPUT_DIR = "./output"
OUTPUT_FORMATS = ["json", "csv", "txt"]  # 支持的输出格式
DEFAULT_OUTPUT_FORMAT = "json"

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = "nga_classifier.log"
