"""
NGA论坛帖子内容分类工具主类
"""

import os
import re
import time
import json
import csv
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

from config import *
from ollama_client import OllamaClient


class NGAClassifier:
    """NGA论坛帖子内容分类工具"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
        # 设置日志
        self._setup_logging()
        
        # 登录状态
        self.is_logged_in = False
        
        # 初始化Ollama客户端
        self.ollama_client = None
        self._init_ollama()
        
        # 尝试加载cookies或登录
        self._init_session()
        
        self.logger.info("NGAClassifier 初始化完成")
    
    def _init_ollama(self):
        """初始化Ollama客户端"""
        try:
            self.ollama_client = OllamaClient()
            self.logger.info("Ollama客户端初始化成功")
        except Exception as e:
            self.logger.error(f"Ollama客户端初始化失败: {e}")
            self.ollama_client = None
    
    def _init_session(self):
        """初始化会话，尝试登录或加载cookies"""
        # 尝试加载保存的cookies
        if USE_COOKIES_FILE and os.path.exists(COOKIES_FILE):
            self.logger.info("尝试加载保存的cookies...")
            if self._load_cookies():
                self.logger.info("Cookies加载成功")
                # 测试是否已登录
                if self._test_login_status():
                    self.logger.info("已成功登录")
                    self.is_logged_in = True
                    return
                else:
                    self.logger.warning("Cookies已失效")
        
        # 如果配置了用户名和密码，尝试登录
        if NGA_USERNAME and NGA_PASSWORD:
            self.logger.info("尝试使用用户名密码登录...")
            if self._login_with_credentials():
                self.logger.info("登录成功")
                self.is_logged_in = True
                # 保存cookies
                if USE_COOKIES_FILE:
                    self._save_cookies()
            else:
                self.logger.error("登录失败")
        else:
            self.logger.warning("未配置登录信息，将尝试匿名访问（可能受限）")
    
    def _load_cookies(self) -> bool:
        """从文件加载cookies"""
        try:
            with open(COOKIES_FILE, 'r') as f:
                cookies_dict = json.load(f)
                self.session.cookies.update(cookies_dict)
                return True
        except Exception as e:
            self.logger.error(f"加载cookies失败: {e}")
            return False
    
    def _save_cookies(self):
        """保存cookies到文件"""
        try:
            cookies_dict = {}
            for cookie in self.session.cookies:
                cookies_dict[cookie.name] = cookie.value
                
            with open(COOKIES_FILE, 'w') as f:
                json.dump(cookies_dict, f)
            self.logger.info("Cookies已保存")
        except Exception as e:
            self.logger.error(f"保存cookies失败: {e}")
    
    def _test_login_status(self) -> bool:
        """测试当前是否已登录"""
        try:
            response = self.session.get(f"{NGA_FORUM_URL}?fid={TARGET_FORUM_ID}", timeout=TIMEOUT)
            return "你必须登录" not in response.text
        except Exception:
            return False
    
    def _login_with_credentials(self) -> bool:
        """使用用户名密码登录"""
        try:
            self.logger.warning("自动登录功能尚未完全实现，请手动设置cookies")
            return False
        except Exception as e:
            self.logger.error(f"登录过程出错: {e}")
            return False
    
    def set_cookies_from_browser(self, cookies_dict: dict):
        """从浏览器手动设置cookies"""
        self.session.cookies.update(cookies_dict)
        if self._test_login_status():
            self.is_logged_in = True
            if USE_COOKIES_FILE:
                self._save_cookies()
            self.logger.info("手动设置的cookies有效，已登录")
            return True
        else:
            self.logger.warning("手动设置的cookies无效")
            return False
    
    def _setup_logging(self):
        """设置日志系统"""
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def fetch_forum_posts(self, 
                         forum_id: str = TARGET_FORUM_ID,
                         max_pages: int = DEFAULT_MAX_PAGES) -> List[Dict]:
        """
        获取指定版块的帖子列表
        
        Args:
            forum_id: 版块ID
            max_pages: 最大爬取页数
            
        Returns:
            帖子信息列表
        """
        self.logger.info(f"开始获取版块 {forum_id} 的帖子，最大页数: {max_pages}")
        
        if not self.is_logged_in:
            self.logger.warning("未登录状态，可能无法获取完整内容")
        
        if max_pages > MAX_PAGES_LIMIT:
            max_pages = MAX_PAGES_LIMIT
            self.logger.warning(f"页数超过限制，调整为 {MAX_PAGES_LIMIT}")
        
        posts = []
        
        for page in range(1, max_pages + 1):
            self.logger.info(f"正在获取第 {page} 页帖子...")
            
            try:
                # 构建版块URL
                params = {
                    'fid': forum_id,
                    'page': page
                }
                
                response = self.session.get(NGA_FORUM_URL, params=params, timeout=TIMEOUT)
                response.raise_for_status()
                
                # 检查是否需要登录
                if "你必须登录" in response.text:
                    self.logger.error("需要登录才能访问版块内容")
                    break
                
                # 解析帖子列表
                page_posts = self._parse_forum_page(response.text)
                
                if not page_posts:
                    self.logger.info(f"第 {page} 页没有找到帖子，停止获取")
                    break
                
                posts.extend(page_posts)
                self.logger.info(f"第 {page} 页获取到 {len(page_posts)} 个帖子")
                
                # 延时
                time.sleep(REQUEST_DELAY)
                
            except Exception as e:
                self.logger.error(f"获取第 {page} 页帖子时出错: {e}")
                continue
        
        self.logger.info(f"版块 {forum_id} 共获取到 {len(posts)} 个帖子")
        return posts
    
    def _parse_forum_page(self, html: str) -> List[Dict]:
        """解析版块页面，提取帖子列表"""
        posts = []
        soup = BeautifulSoup(html, 'lxml')
        
        # NGA论坛的帖子列表在table中
        table_rows = soup.select('table tr')
        
        for row in table_rows:
            try:
                cells = row.find_all('td')
                if len(cells) < 3:  # 至少需要3个单元格
                    continue
                
                # 根据调试结果，NGA的结构是：
                # 单元格1: 回复数
                # 单元格2: 标题链接
                # 单元格3: 作者信息
                
                # 查找帖子标题和链接（通常在第2个单元格）
                title_cell = cells[1] if len(cells) > 1 else cells[0]
                title_link = title_cell.find('a', href=True)
                
                if not title_link:
                    continue
                
                href = title_link.get('href')
                if not href or not ('read.php' in href or 'tid=' in href):
                    continue
                
                title = title_link.get_text().strip()
                if not title or len(title) < 3:  # 过滤太短的标题
                    continue
                
                # 构建完整URL
                if href.startswith('/'):
                    full_url = urljoin(NGA_BASE_URL, href)
                else:
                    full_url = href
                
                # 提取帖子ID
                topic_id = self._extract_topic_id(href)
                
                # 查找作者信息（通常在第3个单元格）
                author = ""
                if len(cells) > 2:
                    cell = cells[2]
                    # 查找用户链接
                    user_link = cell.find('a', href=lambda x: x and 'uid=' in x)
                    if user_link:
                        author = user_link.get_text().strip()
                    else:
                        # 如果没找到用户链接，尝试从文本中提取
                        cell_text = cell.get_text().strip()
                        # 移除数字部分，获取用户名
                        import re
                        clean_text = re.sub(r'\d+', '', cell_text).strip()
                        if clean_text and len(clean_text) > 1:
                            author = clean_text[:20]  # 限制长度
                
                post_info = {
                    'title': title,
                    'url': full_url,
                    'topic_id': topic_id,
                    'author': author or '未知用户'
                }
                
                posts.append(post_info)
                
            except Exception as e:
                self.logger.warning(f"解析帖子元素时出错: {e}")
                continue
        
        # 去重（根据topic_id）
        seen_ids = set()
        unique_posts = []
        for post in posts:
            if post['topic_id'] and post['topic_id'] not in seen_ids:
                seen_ids.add(post['topic_id'])
                unique_posts.append(post)
        
        self.logger.debug(f"解析得到 {len(posts)} 个帖子，去重后 {len(unique_posts)} 个")
        return unique_posts
    
    def _extract_topic_id(self, url: str) -> str:
        """从URL中提取主题ID"""
        patterns = [
            r'tid=(\d+)',
            r'read\.php\?tid=(\d+)',
            r'/thread/(\d+)',
            r'/read/(\d+)',
            r'read\.php.*?tid=(\d+)'  # 支持read.php格式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ""
    
    def fetch_post_content(self, post_url: str, post_title: str) -> Optional[str]:
        """
        获取帖子的具体内容
        
        Args:
            post_url: 帖子URL
            post_title: 帖子标题
            
        Returns:
            帖子内容文本
        """
        try:
            self.logger.debug(f"正在获取帖子内容: {post_title}")
            
            response = self.session.get(post_url, timeout=TIMEOUT)
            response.raise_for_status()
            
            # 解析帖子内容
            content = self._parse_post_content(response.text)
            
            if content and len(content) > MAX_CONTENT_LENGTH:
                content = content[:MAX_CONTENT_LENGTH] + "..."
            
            return content
            
        except Exception as e:
            self.logger.error(f"获取帖子内容失败: {post_title}, 错误: {e}")
            return None
    
    def _parse_post_content(self, html: str) -> Optional[str]:
        """解析帖子内容"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # NGA论坛的帖子内容通常在特定的div中
            # 查找楼主的内容
            content_selectors = [
                '.postcontent',  # 常见的内容class
                '[id^="postcontainer"]',  # ID以postcontainer开头的元素
                '.ubbcode',  # UBB代码容器
                '.quote'  # 引用内容
            ]
            
            content_text = ""
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    # 取第一个元素（通常是楼主内容）
                    first_element = elements[0]
                    content_text = self._clean_content_text(first_element.get_text())
                    if content_text:
                        break
            
            # 如果上述方法都没找到内容，尝试其他方法
            if not content_text:
                # 查找所有可能包含内容的div
                content_divs = soup.find_all('div')
                for div in content_divs:
                    div_text = div.get_text().strip()
                    if len(div_text) > 50 and not any(skip in div_text for skip in ['回复', '引用', '举报']):
                        content_text = self._clean_content_text(div_text)
                        break
            
            return content_text if content_text else None
            
        except Exception as e:
            self.logger.error(f"解析帖子内容失败: {e}")
            return None
    
    def _clean_content_text(self, text: str) -> str:
        """清理内容文本"""
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除常见的无关内容
        remove_patterns = [
            r'\[.*?\]',  # UBB代码
            r'本帖最后由.*?编辑',
            r'使用道具.*?举报',
            r'回复.*?支持.*?反对',
        ]
        
        for pattern in remove_patterns:
            text = re.sub(pattern, '', text)
        
        return text.strip()
    
    def classify_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        对帖子进行分类
        
        Args:
            posts: 帖子列表
            
        Returns:
            包含分类结果的帖子列表
        """
        if not self.ollama_client:
            self.logger.error("Ollama客户端未初始化，无法进行分类")
            return posts
        
        self.logger.info(f"开始对 {len(posts)} 个帖子进行内容分类...")
        
        # 获取帖子内容
        posts_with_content = []
        for i, post in enumerate(posts, 1):
            self.logger.info(f"获取帖子内容 ({i}/{len(posts)}): {post['title'][:50]}...")
            
            content = self.fetch_post_content(post['url'], post['title'])
            post_with_content = post.copy()
            post_with_content['content'] = content or ""
            posts_with_content.append(post_with_content)
            
            time.sleep(REQUEST_DELAY)
        
        # 使用Ollama进行分类
        classified_posts = self.ollama_client.batch_classify(posts_with_content)
        
        self.logger.info("帖子分类完成")
        return classified_posts
    
    def generate_statistics(self, classified_posts: List[Dict]) -> Dict:
        """生成分类统计信息"""
        stats = {
            'total_posts': len(classified_posts),
            'categories': {},
            'keywords': {},
            'authors': {},
            'time_distribution': {},
            'summary': {}
        }
        
        for post in classified_posts:
            classification = post.get('classification', {})
            categories = classification.get('categories', [])
            keywords = classification.get('keywords', [])
            author = post.get('author', '未知')
            
            # 统计分类
            for category in categories:
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # 统计关键词
            for keyword in keywords:
                stats['keywords'][keyword] = stats['keywords'].get(keyword, 0) + 1
            
            # 统计作者
            stats['authors'][author] = stats['authors'].get(author, 0) + 1
            
            # 统计时间分布（按日期）
            if 'parsed_time' in post:
                date_key = post['parsed_time'].strftime('%Y-%m-%d')
                stats['time_distribution'][date_key] = stats['time_distribution'].get(date_key, 0) + 1
        
        # 生成摘要
        stats['summary'] = {
            'most_common_category': max(stats['categories'].items(), key=lambda x: x[1]) if stats['categories'] else None,
            'most_common_keyword': max(stats['keywords'].items(), key=lambda x: x[1]) if stats['keywords'] else None,
            'most_active_author': max(stats['authors'].items(), key=lambda x: x[1]) if stats['authors'] else None,
            'classification_rate': len([p for p in classified_posts if p.get('classification', {}).get('confidence', 0) > 0.5]) / len(classified_posts) if classified_posts else 0
        }
        
        return stats
    
    def save_results(self, classified_posts: List[Dict], stats: Dict, output_dir: str = DEFAULT_OUTPUT_DIR, output_format: str = DEFAULT_OUTPUT_FORMAT):
        """保存分类结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 处理datetime对象序列化问题
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        # 深度处理所有datetime对象
        def process_for_json(data):
            if isinstance(data, dict):
                return {k: process_for_json(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [process_for_json(item) for item in data]
            elif isinstance(data, datetime):
                return data.isoformat()
            return data
        
        if output_format.lower() == 'json':
            # 保存详细结果
            results_file = os.path.join(output_dir, f'nga_classification_{timestamp}.json')
            
            # 处理数据以支持JSON序列化
            json_data = {
                'posts': process_for_json(classified_posts),
                'statistics': process_for_json(stats),
                'generated_at': datetime.now().isoformat()
            }
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"详细结果已保存到: {results_file}")
        
        elif output_format.lower() == 'csv':
            # 保存CSV格式
            csv_file = os.path.join(output_dir, f'nga_classification_{timestamp}.csv')
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['title', 'author', 'time_str', 'url', 'categories', 'keywords', 'confidence']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for post in classified_posts:
                    classification = post.get('classification', {})
                    writer.writerow({
                        'title': post.get('title', ''),
                        'author': post.get('author', ''),
                        'time_str': post.get('time_str', ''),
                        'url': post.get('url', ''),
                        'categories': '; '.join(classification.get('categories', [])),
                        'keywords': '; '.join(classification.get('keywords', [])),
                        'confidence': classification.get('confidence', 0)
                    })
            
            self.logger.info(f"CSV结果已保存到: {csv_file}")
        
        # 保存统计摘要
        summary_file = os.path.join(output_dir, f'nga_summary_{timestamp}.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"NGA二次元国家地理版块内容分析报告\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"="*50 + "\n\n")
            
            f.write(f"总帖子数: {stats['total_posts']}\n\n")
            
            f.write("分类统计:\n")
            for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_posts']) * 100
                f.write(f"  {category}: {count} ({percentage:.1f}%)\n")
            
            f.write("\n热门关键词:\n")
            top_keywords = sorted(stats['keywords'].items(), key=lambda x: x[1], reverse=True)[:10]
            for keyword, count in top_keywords:
                f.write(f"  {keyword}: {count}\n")
            
            f.write("\n活跃作者:\n")
            top_authors = sorted(stats['authors'].items(), key=lambda x: x[1], reverse=True)[:10]
            for author, count in top_authors:
                f.write(f"  {author}: {count}\n")
        
        self.logger.info(f"分析摘要已保存到: {summary_file}")


if __name__ == "__main__":
    # 示例用法
    classifier = NGAClassifier()
    
    # 获取帖子并分类
    posts = classifier.fetch_forum_posts(max_pages=3, time_range_days=7)
    
    if posts:
        classified_posts = classifier.classify_posts(posts)
        stats = classifier.generate_statistics(classified_posts)
        classifier.save_results(classified_posts, stats)
    else:
        print("未获取到任何帖子")
