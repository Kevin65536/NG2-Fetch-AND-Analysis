"""
工具函数模块
"""

import os
import re
import json
from typing import List, Dict
from urllib.parse import urlparse, urljoin


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原文件名
        max_length: 最大长度
        
    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
    
    # 移除首尾空格和点号
    filename = filename.strip('. ')
    
    # 限制长度
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        name = name[:max_length - len(ext) - 1]
        filename = name + ext
    
    return filename or 'unnamed'


def extract_filename_from_url(url: str, default_ext: str = '.jpg') -> str:
    """
    从URL提取文件名
    
    Args:
        url: 图片URL
        default_ext: 默认扩展名
        
    Returns:
        文件名
    """
    try:
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        
        if not filename or '.' not in filename:
            # 尝试从查询参数中提取
            if 'filename=' in parsed.query:
                match = re.search(r'filename=([^&]+)', parsed.query)
                if match:
                    filename = match.group(1)
            
            # 如果还是没有，使用默认名称
            if not filename or '.' not in filename:
                filename = f"image_{hash(url) % 10000}{default_ext}"
        
        return sanitize_filename(filename)
    
    except:
        return f"image_{hash(url) % 10000}{default_ext}"


def load_json_file(file_path: str) -> Dict:
    """
    加载JSON文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        JSON数据
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def save_json_file(data: Dict, file_path: str):
    """
    保存JSON文件
    
    Args:
        data: 数据
        file_path: 文件路径
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存JSON文件失败: {e}")


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化后的大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    创建进度条
    
    Args:
        current: 当前进度
        total: 总数
        width: 进度条宽度
        
    Returns:
        进度条字符串
    """
    if total == 0:
        return "[" + "=" * width + "] 100.0%"
    
    percent = current / total
    filled = int(width * percent)
    bar = "=" * filled + "-" * (width - filled)
    return f"[{bar}] {percent * 100:.1f}% ({current}/{total})"


def parse_nga_topic_id(url: str) -> str:
    """
    从NGA主题URL中解析主题ID
    
    Args:
        url: 主题URL
        
    Returns:
        主题ID
    """
    patterns = [
        r'tid=(\d+)',
        r'/thread/(\d+)',
        r'read\.php\?tid=(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return ""


def parse_nga_user_id(url: str) -> str:
    """
    从NGA用户URL中解析用户ID
    
    Args:
        url: 用户URL
        
    Returns:
        用户ID
    """
    patterns = [
        r'uid=(\d+)',
        r'/user/(\d+)',
        r'nuke\.php\?func=ucp&uid=(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return ""


def is_image_url(url: str) -> bool:
    """
    检查URL是否为图片URL
    
    Args:
        url: URL
        
    Returns:
        是否为图片URL
    """
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # 检查文件扩展名
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
        if any(path.endswith(ext) for ext in image_extensions):
            return True
        
        # 检查域名（一些图床服务）
        image_domains = ['imgur.com', 'img.nga.cn', 'pic.nga.cn']
        if any(domain in parsed.netloc for domain in image_domains):
            return True
        
        return False
    except:
        return False
