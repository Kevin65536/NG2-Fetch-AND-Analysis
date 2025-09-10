"""
NGA论坛帖子内容分类工具命令行入口
"""

import argparse
import sys
from nga_classifier import NGAClassifier
from config import TARGET_FORUM_ID, DEFAULT_MAX_PAGES


def main():
    parser = argparse.ArgumentParser(description='NGA论坛帖子内容分类工具')
    
    parser.add_argument('-f', '--forum-id', default=None,
                       help=f'版块ID (默认: {TARGET_FORUM_ID} - 二次元国家地理)')
    parser.add_argument('-o', '--output', default='./output', 
                       help='输出目录 (默认: ./output)')
    parser.add_argument('-p', '--pages', type=int, default=DEFAULT_MAX_PAGES,
                       help=f'最大爬取页数 (默认: {DEFAULT_MAX_PAGES})')
    parser.add_argument('--format', choices=['json', 'csv', 'txt'], default='json',
                       help='输出格式 (默认: json)')
    parser.add_argument('--delay', type=float,
                       help='请求延时秒数 (覆盖配置文件设置)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出模式')
    parser.add_argument('--test-ollama', action='store_true',
                       help='测试Ollama连接')
    
    args = parser.parse_args()
    
    # 测试Ollama连接
    if args.test_ollama:
        from ollama_client import test_ollama_connection
        success = test_ollama_connection()
        sys.exit(0 if success else 1)
    
    # 应用命令行参数
    if args.delay is not None:
        import config
        config.REQUEST_DELAY = args.delay
        
    if args.verbose:
        import config
        config.LOG_LEVEL = "DEBUG"
    
    try:
        # 创建分类器实例
        classifier = NGAClassifier()
        
        # 确定版块ID
        forum_id = args.forum_id or TARGET_FORUM_ID
        
        print(f"开始分析NGA版块 {forum_id}...")
        print(f"最大页数: {args.pages}")
        
        # 获取帖子列表（基于页面）
        posts = classifier.fetch_forum_posts(
            forum_id=forum_id,
            max_pages=args.pages
        )
        
        if not posts:
            print("未获取到任何帖子，请检查版块ID和登录状态")
            sys.exit(1)
        
        print(f"获取到 {len(posts)} 个帖子，开始内容分类...")
        
        # 进行分类
        classified_posts = classifier.classify_posts(posts)
        
        # 生成统计
        stats = classifier.generate_statistics(classified_posts)
        
        # 保存结果
        classifier.save_results(classified_posts, stats, args.output, args.format)
        
        # 显示简要统计
        print("\n=== 分类统计 ===")
        print(f"总帖子数: {stats['total_posts']}")
        
        if stats['categories']:
            print("\n分类分布:")
            for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_posts']) * 100
                print(f"  {category}: {count} ({percentage:.1f}%)")
        
        if stats['summary']['most_common_keyword']:
            print(f"\n最热关键词: {stats['summary']['most_common_keyword'][0]} ({stats['summary']['most_common_keyword'][1]}次)")
        
        print(f"\n结果已保存到: {args.output}")
        print("分析完成!")
        
    except KeyboardInterrupt:
        print("\n用户中断，退出程序")
        sys.exit(1)
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
