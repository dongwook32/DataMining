import urllib.request
import re

url = 'https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002579321'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        for line in html.splitlines():
            line_s = line.strip()
            if any(k in line_s for k in ['거시경제', '김수현', '26', '1-70', '1-85', '10.22823', '페이지', 'page']):
                print(line_s[:120])
except Exception as e:
    print('Error:', e)

