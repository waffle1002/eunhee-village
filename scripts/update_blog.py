"""네이버 블로그 RSS를 읽어서 blog-feed.json 과 thumbs/ 썸네일을 만든다.
GitHub Actions(.github/workflows/blog.yml)가 매일 돌린다. 직접 돌려도 된다: python3 scripts/update_blog.py
"""
import html, io, json, os, re, sys, time, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

BLOG = 'waffle95'
RSS = f'https://rss.blog.naver.com/{BLOG}.xml'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'blog-feed.json')
THUMBS = os.path.join(ROOT, 'thumbs')
# 홈페이지에 올리지 않는 카테고리 (투자 글, 다이어트 기록은 빼기로 함)
SKIP = ('투자', '다이어트')
UA = {'User-Agent': 'Mozilla/5.0 (eunhee-village blog sync)', 'Referer': f'https://blog.naver.com/{BLOG}'}


def get(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def shelf_of(cat, title):
    if '히말라야' in cat or '히말라야' in title:
        return 'himalaya'
    if '포토덤프' in cat:
        return 'photodump'
    if cat.strip() == '책':
        return 'books'
    if 'AI' in cat:
        return 'ai'
    return 'etc'


def clean(text, n=70):
    text = re.sub(r'<[^>]+>', ' ', html.unescape(text or ''))
    text = re.sub(r'\s+', ' ', text).strip()
    return text if len(text) <= n else text[:n].rstrip() + '...'


def post_id(link):
    m = re.search(r'/(\d{9,})', link or '') or re.search(r'logNo=(\d+)', link or '')
    return m.group(1) if m else ''


def find_image(desc, pid):
    m = re.search(r'<img[^>]+src=["\']([^"\']+)', html.unescape(desc or ''))
    if m:
        return m.group(1)
    try:  # 본문 첫 사진: 모바일 페이지의 og:image
        page = get(f'https://m.blog.naver.com/{BLOG}/{pid}').decode('utf-8', 'ignore')
        m = re.search(r'property="og:image"\s+content="([^"]+)"', page)
        return html.unescape(m.group(1)) if m else ''
    except Exception as e:
        print('  og:image 실패', pid, e)
        return ''


def save_thumb(url, pid):
    path = os.path.join(THUMBS, f'{pid}.jpg')
    if os.path.exists(path):
        return f'thumbs/{pid}.jpg'
    if not url:
        return ''
    try:
        raw = get(re.sub(r'\?type=\w+$', '', url) + '?type=w400')
    except Exception:
        try:
            raw = get(url)
        except Exception as e:
            print('  썸네일 실패', pid, e)
            return ''
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert('RGB')
        im.thumbnail((240, 240))
        os.makedirs(THUMBS, exist_ok=True)
        im.save(path, 'JPEG', quality=78, optimize=True)
    except Exception as e:
        print('  썸네일 변환 실패', pid, e)
        return ''
    return f'thumbs/{pid}.jpg'


def main():
    root = ET.fromstring(get(RSS))
    posts = []
    for it in root.iter('item'):
        cat = (it.findtext('category') or '').strip()
        title = clean(it.findtext('title'), 120)
        if any(s in cat for s in SKIP):
            continue
        link = (it.findtext('link') or '').split('?')[0]
        pid = post_id(it.findtext('link') or it.findtext('guid'))
        if not pid:
            continue
        try:
            date = parsedate_to_datetime(it.findtext('pubDate')).strftime('%Y.%m.%d')
        except Exception:
            date = ''
        desc = it.findtext('description') or ''
        posts.append({
            'id': pid, 'title': title, 'date': date, 'cat': cat, 'shelf': shelf_of(cat, title),
            'ex': clean(desc), 'url': f'https://blog.naver.com/{BLOG}/{pid}',
            'thumb': save_thumb(find_image(desc, pid), pid),
        })
        time.sleep(0.3)
    if not posts:
        print('글을 하나도 못 읽었어요. 기존 파일을 그대로 둬요.')
        return 1
    old = {}
    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding='utf-8'))
    data = {'updated': old.get('updated', ''), 'posts': posts}
    if old.get('posts') != posts:
        data['updated'] = time.strftime('%Y-%m-%dT%H:%M:%S+09:00', time.gmtime(time.time() + 9 * 3600))
    json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(posts)}개 글, 썸네일 {sum(1 for p in posts if p["thumb"])}개')
    return 0


if __name__ == '__main__':
    sys.exit(main())
