import requests
import time
import random
import os
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class JapaneseGrammarScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()

        # 配置超时重试策略 (总超时>30s)
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 创建存储目录
        os.makedirs("grammar_pages", exist_ok=True)

    def _random_delay(self):
        """随机延迟1-5秒模拟人工操作"""
        delay = random.uniform(1, 5)
        time.sleep(delay)

    def _get_random_headers(self):
        """生成随机浏览器请求头"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def scrape_page(self, page_id):
        """抓取单个语法页面"""
        url = f"https://share.jiemo.net/NSeries/grammarShare?version=2260&isReview=0&at=12&dt=1&uc=store_huawei&id={page_id}&share=1"

        try:
            # 设置超时参数(连接15s + 读取25s = 总超时40s)
            response = self.session.get(
                url,
                headers=self._get_random_headers(),
                timeout=(15, 25)
            )
            response.raise_for_status()

            # 解析目标内容
            soup = BeautifulSoup(response.content, 'lxml')
            grammar_content = soup.find('div', class_='grammar-content')

            if grammar_content:
                # 保存完整HTML结构
                filename = f"grammar_pages/{str(page_id).zfill(4)}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(str(grammar_content))
                return True
            return False

        except (requests.exceptions.RequestException, Exception) as e:
            print(f"ID {page_id} 抓取失败: {str(e)}")
            return False

    def run(self, start_id=1, max_consecutive_fails=20):
        """启动抓取任务"""
        consecutive_fails = 0
        current_id = start_id

        while consecutive_fails < max_consecutive_fails:
            self._random_delay()
            success = self.scrape_page(current_id)

            if success:
                print(f"成功保存: {str(current_id).zfill(4)}.html")
                consecutive_fails = 0
            else:
                consecutive_fails += 1
                print(f"连续失败次数: {consecutive_fails}/{max_consecutive_fails}")

            current_id += 1

        print(f"\n抓取完成! 从ID {start_id} 开始共抓取 {current_id - start_id - consecutive_fails} 个页面")


if __name__ == "__main__":
    scraper = JapaneseGrammarScraper()
    scraper.run()
