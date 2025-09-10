# NGA帖子内容分类工具

这是一个专门用于分析NGA论坛"二次元国家地理"版块帖子内容的工具，通过集成本地Ollama大语言模型，自动对帖子进行二次元内容分类，生成统计报告。

## 功能特点

- 🎯 专门针对NGA"二次元国家地理"版块
- 📅 支持按时间范围过滤帖子
- 🤖 集成Ollama本地大模型进行智能分类
- 📊 生成详细的分类统计报告
- 💾 支持多种输出格式（JSON、CSV、TXT）
- 🔒 支持cookie登录访问

## 环境要求

### Python环境
- Python 3.8+
- 依赖库见 `requirements.txt`

### Ollama环境
1. 安装Ollama：访问 [https://ollama.com](https://ollama.com) 下载安装
2. 下载中文模型（推荐）：
   ```bash
   ollama pull qwen2.5:latest
   ```

## 使用方法

### 命令行使用

基本用法：
```bash
python main.py
```

完整参数：
```bash
python main.py -f -7 -p 5 -d 30 --format json -o ./output
```

参数说明：
- `-f, --forum-id`: 版块ID（默认使用配置文件中的设置）
- `-p, --pages`: 最大爬取页数（默认5页）
- `-d, --days`: 时间范围天数（默认30天）
- `--format`: 输出格式（json/csv/txt，默认json）
- `-o, --output`: 输出目录（默认./output）
- `-v, --verbose`: 详细日志模式
- `--test-ollama`: 测试Ollama连接

### 配置登录

由于NGA可能需要登录，建议手动设置cookies：

```python
from nga_classifier import NGAClassifier

classifier = NGAClassifier()
cookies = {
    'ngaPassportUid': 'your_uid',
    'ngaPassportCid': 'your_cid',
    # ... 其他cookie字段
}
classifier.set_cookies_from_browser(cookies)
```

## 分类体系

默认分类包括：
1. **动画/番剧** - 动画作品讨论
2. **游戏** - 游戏相关内容  
3. **漫画** - 漫画作品讨论
4. **轻小说** - 轻小说相关
5. **虚拟主播/VTuber** - VTuber相关
6. **手办/周边** - 实体商品
7. **音乐/歌曲** - 音乐相关
8. **其他** - 其他二次元内容

## 安装与配置

1. 安装依赖：`pip install -r requirements.txt`
2. 启动Ollama：`ollama serve` 
3. 测试连接：`python main.py --test-ollama`
4. 配置登录信息（如需要）
5. 运行分析：`python main.py`

详细说明请查看项目文档。
