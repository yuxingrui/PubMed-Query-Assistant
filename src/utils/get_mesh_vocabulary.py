import requests
from bs4 import BeautifulSoup

def scrape_anchor_text_with_bold(term):
    # 发送 GET 请求获取网页内容
    url = "https://www.ncbi.nlm.nih.gov/mesh/?term="+str(term)
    response = requests.get(url)
    
    # 检查响应状态码
    if response.status_code == 200:
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有的 <a> 标签
        anchor_tags = soup.find_all('a')
        
        # 筛选包含 <b> 标签的 <a> 标签，并获取文本内容
        anchor_texts_with_bold = [anchor.text for anchor in anchor_tags if anchor.find('b') is not None]
        
        return anchor_texts_with_bold
    else:
        print("Failed to fetch the page:", response.status_code)
        return None
def get_mesh_list(keywords:str)->str:
    items=keywords.split(',')
    final=[]
    for item in items:
        temp=scrape_anchor_text_with_bold(item)
        final+=temp
    res=','.join(final)
    return res