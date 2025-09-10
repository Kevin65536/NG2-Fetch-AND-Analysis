"""
Ollama客户端模块
用于与本地Ollama服务进行通信，实现文本分类功能
"""

import json
import logging
import requests
from typing import Dict, List, Optional
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT, CLASSIFICATION_PROMPT


class OllamaClient:
    """Ollama客户端类"""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # 检查Ollama服务是否可用
        self._check_service()
    
    def _check_service(self) -> bool:
        """检查Ollama服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            
            # 检查模型是否存在
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            if self.model not in model_names:
                self.logger.warning(f"模型 {self.model} 未找到，可用模型: {model_names}")
                self.logger.warning("请确保已安装所需模型，或修改配置文件中的OLLAMA_MODEL")
                return False
            
            self.logger.info(f"Ollama服务连接成功，使用模型: {self.model}")
            return True
            
        except Exception as e:
            self.logger.error(f"无法连接到Ollama服务: {e}")
            self.logger.error(f"请确保Ollama服务正在运行于 {self.base_url}")
            return False
    
    def classify_content(self, title: str, content: str) -> Optional[Dict]:
        """
        对帖子内容进行分类
        
        Args:
            title: 帖子标题
            content: 帖子内容
            
        Returns:
            分类结果字典，包含categories、keywords、confidence字段
        """
        try:
            # 构建提示词
            prompt = CLASSIFICATION_PROMPT.format(title=title, content=content)
            
            # 调用Ollama API
            response = self._call_ollama(prompt)
            
            if not response:
                return None
            
            # 解析响应
            result = self._parse_classification_result(response)
            return result
            
        except Exception as e:
            self.logger.error(f"分类内容时出错: {e}")
            return None
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """调用Ollama API"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # 降低温度以获得更一致的结果
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=OLLAMA_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except Exception as e:
            self.logger.error(f"调用Ollama API失败: {e}")
            return None
    
    def _parse_classification_result(self, response: str) -> Dict:
        """解析分类结果，确保分类互斥"""
        try:
            # 尝试提取JSON部分
            response = response.strip()
            
            # 查找JSON块
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # 验证必需字段
                if 'categories' not in result:
                    result['categories'] = []
                if 'keywords' not in result:
                    result['keywords'] = []
                if 'confidence' not in result:
                    result['confidence'] = 0.5
                
                # 确保分类互斥性：只保留第一个分类
                if isinstance(result['categories'], list) and len(result['categories']) > 1:
                    self.logger.warning(f"检测到多个分类 {result['categories']}，只保留第一个以确保互斥性")
                    result['categories'] = [result['categories'][0]]
                
                return result
            else:
                # 如果无法解析JSON，尝试从文本中提取信息
                return self._fallback_parse(response)
                
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON解析失败，尝试备用解析: {e}")
            return self._fallback_parse(response)
        except Exception as e:
            self.logger.error(f"解析分类结果失败: {e}")
            return {"categories": [], "keywords": [], "confidence": 0.0}
    
    def _fallback_parse(self, response: str) -> Dict:
        """备用解析方法，当JSON解析失败时使用，确保分类互斥"""
        result = {
            "categories": [],
            "keywords": [], 
            "confidence": 0.3
        }
        
        # 尝试从文本中提取分类信息，按优先级顺序检查
        response_lower = response.lower()
        
        # 按优先级检查分类，只选择第一个匹配的
        if any(word in response_lower for word in ['动画', '番剧', 'anime']):
            result['categories'] = ['动画/番剧']
        elif any(word in response_lower for word in ['游戏', 'game', '手游']):
            result['categories'] = ['游戏']
        elif any(word in response_lower for word in ['漫画', 'manga']):
            result['categories'] = ['漫画']
        elif any(word in response_lower for word in ['轻小说', '小说', 'novel']):
            result['categories'] = ['轻小说']
        elif any(word in response_lower for word in ['vtuber', '虚拟主播', '主播']):
            result['categories'] = ['虚拟主播/VTuber']
        elif any(word in response_lower for word in ['手办', '周边', 'figure']):
            result['categories'] = ['手办/周边']
        elif any(word in response_lower for word in ['音乐', '歌曲', 'music']):
            result['categories'] = ['音乐/歌曲']
        else:
            # 如果没有找到明确分类，标记为其他
            result['categories'] = ['其他']
        
        self.logger.debug(f"备用解析结果（互斥）: {result}")
        return result
    
    def batch_classify(self, posts: List[Dict]) -> List[Dict]:
        """
        批量分类帖子
        
        Args:
            posts: 帖子列表，每个元素包含title和content字段
            
        Returns:
            分类结果列表
        """
        results = []
        
        for i, post in enumerate(posts, 1):
            self.logger.info(f"正在分类第 {i}/{len(posts)} 个帖子: {post.get('title', '无标题')[:50]}...")
            
            classification = self.classify_content(
                post.get('title', ''),
                post.get('content', '')
            )
            
            if classification:
                # 将分类结果添加到帖子信息中
                post_result = post.copy()
                post_result.update({
                    'classification': classification,
                    'processed_at': self._get_current_time()
                })
                results.append(post_result)
            else:
                # 如果分类失败，添加默认结果
                post_result = post.copy()
                post_result.update({
                    'classification': {
                        'categories': ['其他'],
                        'keywords': [],
                        'confidence': 0.0
                    },
                    'processed_at': self._get_current_time(),
                    'error': '分类失败'
                })
                results.append(post_result)
        
        return results
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 测试函数
def test_ollama_connection():
    """测试Ollama连接"""
    client = OllamaClient()
    
    # 测试分类功能
    test_title = "【讨论】最近看的新番推荐"
    test_content = "最近在看鬼灭之刃最新季，画质真的很棒，推荐大家去看看。另外还有咒术回战也很不错。"
    
    result = client.classify_content(test_title, test_content)
    print(f"测试分类结果: {result}")
    
    return result is not None


if __name__ == "__main__":
    test_ollama_connection()
