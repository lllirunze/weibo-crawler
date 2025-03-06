import requests
import pandas as pd
import os
from bs4 import BeautifulSoup
from datetime import datetime

# 微博热搜 URL
URL = "https://s.weibo.com/top/summary?cate=realtimehot"

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cookie": "SUB=_2AkMQyRPJf8NxqwFRmf8Ry27rb49_zAHEieKmleISJRMxHRl-yT9kqmYatRB6O0k9JnzofRZMctfVkDf1xx0d17jzPRAp; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWKlzaX.QZFSPs6zb4bK4.5; _s_tentry=passport.weibo.com; Apache=2728838988131.0146.1737858304629; SINAGLOBAL=2728838988131.0146.1737858304629; ULV=1737858304643:1:1:1:2728838988131.0146.1737858304629:"
}

def fetch_weibo_hotsearch(url, headers):
    """爬取微博热搜页面"""
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"请求失败，状态码: {response.status_code}")
        return None
    
def parse_hotsearch(html):
    """解析微博热搜内容"""
    soup = BeautifulSoup(html, "html.parser")
    hotsearch_list = []
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")[1:]  # 跳过表头
        for row in rows:
            keyword = row.find("td", class_="td-02")
            hot_value = row.find("td", class_="td-03")

            hotsearch_list.append({
                "Keyword": keyword.a.get_text(strip=True) if keyword and keyword.a else "-",
                "Link": f"https://s.weibo.com{keyword.a['href']}" if keyword and keyword.a and 'href' in keyword.a.attrs else "-",
                "Hot Value": hot_value.get_text(strip=True) if hot_value else "-"
            })
    return hotsearch_list

def save_to_markdown(data):
    """保存数据到Markdown文件"""
    today = datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

    # 创建文件夹结构
    folder_path = os.path.join("archive", year, month)
    os.makedirs(folder_path, exist_ok=True)

    # 文件路径
    filename = os.path.join(folder_path, f"{day}.md")
    title = f"{year}年{month}月{day}日-微博热搜"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        for item in data:
            if item['Hot Value']:
                f.write(f"- [{item['Keyword']}]({item['Link']}) - [{item['Hot Value']}]\n")
            else:
                f.write(f"- [{item['Keyword']}]({item['Link']})\n")
    print(f"数据已保存到 {filename}")

    # 更新根目录的README.md
    readme_path = "README.md"
    rank = 0
    with open(readme_path, "w", encoding="utf-8") as readme:
        readme.write(f"# {title}\n\n")
        for item in data:
            rank += 1
            if item['Hot Value']:
                readme.write(f"{rank}. [{item['Keyword']}]({item['Link']}) - [{item['Hot Value']}]\n")
            else:
                readme.write(f"{rank}. [{item['Keyword']}]({item['Link']})\n")
    print(f"当天热搜已追加到根目录的 {readme_path}")

html = fetch_weibo_hotsearch(URL, HEADERS)
if html:
    print("解析热搜内容...")
    hotsearch_data = parse_hotsearch(html)
    if hotsearch_data:
        print("保存热搜到文件...")
        save_to_markdown(hotsearch_data)
    else:
        print("未能解析到热搜数据。")
else:
    print("未能获取微博热搜页面。")