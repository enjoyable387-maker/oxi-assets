from pathlib import Path
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import urlparse,parse_qs,urlencode,urlunparse
import urllib.request,xml.etree.ElementTree as ET,json,re,sys,shutil
HERE=Path(__file__).resolve().parent
BLOG='https://blog.naver.com/oxi_studio'
BASE='https://raw.githubusercontent.com/enjoyable387-maker/oxi-assets/main/columns'
sys.path.insert(0,str(HERE/'renderer'))
import covers
covers.OUT=HERE/'covers'
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.images = []
    def handle_data(self, data): self.parts.append(data)
    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            src = dict(attrs).get('src', '')
            if urlparse(src).hostname and urlparse(src).hostname.endswith('.pstatic.net'):
                self.images.append(src)

def classify(title):
    if any(word in title for word in ['운영', '관리', '갱신', '만료', '업데이트', '변경 기록', '오픈 뒤', '조회수', '성과', '보고서', '기준선']):
        return '운영·관리'
    if any(word in title for word in ['시공 사례', '사진', '메뉴', '소개 글', '문의', '랜딩', '속도', '플레이스', '포트폴리오', '홈페이지 구성']):
        return '홈페이지 설계'
    return '제작 전 알아두기'

def parse_feed(xml):
    root = ET.fromstring(xml)
    items = root.findall('./channel/item')
    posts = []
    for item in items:
        title = (item.findtext('title') or '').strip()
        category = (item.findtext('category') or '').replace('\xa0', ' ').strip()
        compact = re.sub(r'\s+', '', category)
        if compact not in {'홈페이지제작', '인테리어', '포트폴리오', 'etc'}:
            continue
        if compact == 'etc' and not any(word in title for word in ['홈페이지', '제작', '포트폴리오']):
            continue
        link = (item.findtext('guid') or item.findtext('link') or '').strip()
        match = re.fullmatch(r'https://blog\.naver\.com/oxi_studio/(\d+)(?:\?.*)?', link)
        if not match: continue
        post_id = match.group(1)
        content = Text(); content.feed(item.findtext('description') or '')
        summary = re.sub(r'\s+', ' ', ''.join(content.parts)).strip()
        summary = re.split(r'\s*■\s*', summary)[0]
        summary = re.sub(r'\.{3,}$', '', summary).strip()
        if len(summary) > 155:
            summary = summary[:155].rsplit(' ', 1)[0].rstrip('.,') + '…'
        date = parsedate_to_datetime(item.findtext('pubDate')).isoformat()
        image = content.images[0] if content.images else ''
        if image:
            parsed = urlparse(image)
            # Use the same public thumbnail variant as Naver's og:image metadata.
            params = parse_qs(parsed.query); params['type'] = ['w2']
            image = urlunparse(parsed._replace(scheme='https', query=urlencode(params, doseq=True)))
        posts.append({'id': post_id, 'title': title, 'summary': summary, 'url': BLOG + '/' + post_id,
                      'publishedAt': date, 'category': classify(title), 'sourceCategory': category,
                      'imageSource': image, 'image': '/media/column/' + post_id + '.jpg' if image else ''})
    return posts, len(items)
def refresh():
 req=urllib.request.Request('https://rss.blog.naver.com/oxi_studio.xml',headers={'User-Agent':'OXI-Column-Sync/1.0 (+https://oxi.kr/column)'})
 with urllib.request.urlopen(req,timeout=30) as response: xml=response.read()
 incoming,count=parse_feed(xml)
 if not incoming: raise ValueError('RSS returned no eligible OXI articles; existing archive retained')
 old=json.loads((HERE/'feed.json').read_text())
 archive={p['id']:p for p in old['posts']}
 for p in incoming: archive[p['id']]=p
 posts=covers.build_covers(sorted(archive.values(),key=lambda p:p['publishedAt'],reverse=True))
 for p in posts:
  p.pop('imageSource',None)
  p['image']=BASE+'/covers/'+p['id']+'.svg'+('?'+p['image'].split('?',1)[1] if '?' in p['image'] else '')
 # A daily checkpoint keeps a quiet public repository's schedule active without minute-by-minute commits.
 today=datetime.now(timezone.utc).date().isoformat()
 if posts==old['posts'] and str(old.get('lastSuccess','')).startswith(today):
  print('RSS checked successfully; no article changes.');return
 result={'posts':posts,'lastSuccess':datetime.now(timezone.utc).isoformat(),'sourceCount':count,'status':'live','refreshSeconds':900}
 temp=HERE/'feed.tmp';temp.write_text(json.dumps(result,ensure_ascii=False,indent=2));temp.replace(HERE/'feed.json')
 print(f'RSS sync successful: {len(incoming)} eligible from {count} RSS items; {len(posts)} archived articles')
if __name__=='__main__': refresh()
