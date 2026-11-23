"""Collect public occupational-health RSS news. No secrets or personal data."""
import json, re, hashlib, html
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote
import feedparser
import requests

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'news.json'
KST = timezone(timedelta(hours=9))
CATEGORIES = {
 '뉴스': ['산업보건 직업병 건강검진', '근로자 건강관리 직무스트레스'],
 '법령·입법예고': ['산업안전보건법 개정 입법예고', '고용노동부 산업안전보건 고시 개정'],
 '화학물질 규제': ['MSDS 화학물질 노출기준 규제', '산업안전보건 화학물질 관리'],
 '공지·지침': ['고용노동부 산업보건 공지', '안전보건공단 보건관리 지침'],
 '재해·직업병 사례': ['산업재해 직업병 사례', '근로자 직업성 질병 재해 사례'],
 '지원사업': ['안전보건공단 건강증진 지원사업', '고용노동부 산업보건 지원사업'],
 '채용': ['보건관리자 채용', '산업간호사 채용'],
 '정보·자료': ['KOSHA GUIDE 산업보건 자료', '산업보건 교육 세미나 자료'],
}
HEADERS = {'User-Agent': 'HealthDaily/2.0 (public RSS reader)'}
MAX_DAYS = 30
IMPORTANT = ['산업안전보건법 개정', '산업안전보건법 시행', '시행규칙 개정', '시행령 개정', '입법예고', '고시 개정', '노출기준 개정', '특수건강진단', '작업환경측정', '중대재해', '직업병 인정', 'msds 의무', '물질안전보건자료 의무']
RELEVANT = ['산업보건', '보건관리자', '산업안전보건', '근로자 건강', '직업병', '직업성 질병', '특수건강진단', '건강진단', '건강검진', '작업환경측정', 'msds', '물질안전보건자료', '노출기준', '화학물질', '근골격계', '직무스트레스', '안전보건공단', '고용노동부', 'kosha', '산업간호사', '산업재해', '중대재해', '직업성', '직업건강', '안전보건', '유해인자']
WEAK = ['교육', '세미나', '채용', '지원사업', '가이드', '자료', '설명회', '모집']

def clean(value):
    value = re.sub(r'<[^>]+>', ' ', value or '')
    return re.sub(r'\s+', ' ', html.unescape(value)).strip()

def date_of(entry):
    from calendar import timegm
    for field in ('published_parsed', 'updated_parsed'):
        t = entry.get(field)
        if t:
            return datetime.fromtimestamp(timegm(t), timezone.utc)
    return None

def classify(item):
    text = (item.get('title', '') + ' ' + item.get('summary', '')).lower()
    title = item.get('title', '').lower()
    important = any(k.lower() in title for k in IMPORTANT)
    matches = sum(k.lower() in text for k in RELEVANT)
    if important and matches:
        return '중요', True
    if matches >= 2 or (matches >= 1 and item.get('category') in ('법령·입법예고', '화학물질 규제', '재해·직업병 사례')):
        return '일반', True
    if matches >= 1 or (item.get('category') in ('채용', '정보·자료', '지원사업') and any(k in text for k in WEAK) and matches):
        return '참고', True
    return '참고', False

def main():
    existing = []
    if DATA.exists():
        try:
            loaded = json.loads(DATA.read_text(encoding='utf-8'))
            existing = loaded if isinstance(loaded, list) else loaded.get('items', [])
        except (ValueError, TypeError):
            print('[WARN] Existing news.json could not be parsed; keeping file untouched is recommended.')
            raise
    by_id = {x['id']: x for x in existing if isinstance(x, dict) and x.get('id')}
    now = datetime.now(timezone.utc)
    stats = {}
    for category, queries in CATEGORIES.items():
        count = 0
        for query in queries:
            url = 'https://news.google.com/rss/search?q=' + quote(query + ' when:7d') + '&hl=ko&gl=KR&ceid=KR:ko'
            try:
                response = requests.get(url, headers=HEADERS, timeout=20)
                response.raise_for_status()
                feed = feedparser.parse(response.content)
                for entry in feed.entries[:25]:
                    link = entry.get('link', '')
                    if not link.startswith('https://'):
                        continue
                    published = date_of(entry)
                    if published and (now - published).days > MAX_DAYS:
                        continue
                    title = clean(entry.get('title', ''))
                    if not title:
                        continue
                    uid = hashlib.sha256((category + '|' + link).encode()).hexdigest()[:20]
                    if uid in by_id:
                        continue
                    summary = clean(entry.get('summary', ''))[:240]
                    item = {'id': uid, 'category': category, 'title': title, 'url': link,
                            'date': (published or now).astimezone(KST).strftime('%Y-%m-%d'),
                            'summary': summary or '원문에서 상세 내용을 확인하세요.',
                            'source': clean(entry.get('source', {}).get('title', '')) or 'Google 뉴스 RSS',
                            'collected_at': now.astimezone(KST).isoformat()}
                    priority, relevant = classify(item)
                    if not relevant:
                        continue
                    item['priority'] = priority
                    by_id[uid] = item
                    count += 1
            except (requests.RequestException, ValueError) as exc:
                print(f'[WARN] {category}: {exc}')
        stats[category] = count
    # Keep existing articles; classify them for display without discarding historical records.
    for item in by_id.values():
        item['priority'] = classify(item)[0]
    cutoff = (now - timedelta(days=90)).astimezone(KST).strftime('%Y-%m-%d')
    items = [x for x in by_id.values() if x.get('date', '') >= cutoff]
    items.sort(key=lambda x: (x.get('date', ''), x.get('collected_at', '')), reverse=True)
    DATA.write_text(json.dumps(items[:1500], ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('New:', stats, 'Total:', len(items[:1500]))

if __name__ == '__main__':
    main()
