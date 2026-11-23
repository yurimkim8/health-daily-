"""Public RSS collection; no personal data, secrets, or paid APIs required."""
import json, os, re, hashlib, html
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote, urlparse
import feedparser
import requests

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'news.json'
KST=timezone(timedelta(hours=9))
CATEGORIES={
 '뉴스': ['산업보건 직업병 건강검진', '근로자 건강관리 직무스트레스'],
 '법령·입법예고': ['산업안전보건법 개정 입법예고', '고용노동부 산업안전보건 고시 개정'],
 '화학물질 규제': ['MSDS 화학물질 노출기준 규제', '산업안전보건 화학물질 관리'],
 '공지·지침': ['고용노동부 산업보건 공지', '안전보건공단 보건관리 지침'],
 '재해·직업병 사례': ['산업재해 직업병 사례', '근로자 직업성 질병 재해 사례'],
 '지원사업': ['안전보건공단 건강증진 지원사업', '고용노동부 산업보건 지원사업'],
 '채용': ['보건관리자 채용', '산업간호사 채용'],
 '정보·자료': ['KOSHA GUIDE 산업보건 자료', '산업보건 교육 세미나 자료'],
}
HEADERS={'User-Agent':'HealthDaily/1.0 (public RSS reader)'}
MAX_DAYS=30

def clean(value):
    value=re.sub(r'<[^>]+>',' ',value or '')
    return re.sub(r'\s+',' ',html.unescape(value)).strip()

def date_of(entry):
    for field in ('published_parsed','updated_parsed'):
        t=entry.get(field)
        if t:
            from calendar import timegm
            return datetime.fromtimestamp(timegm(t),timezone.utc)
    return None

def main():
    existing=[]
    if DATA.exists():
        try:
            loaded=json.loads(DATA.read_text(encoding='utf-8'))
            existing=loaded if isinstance(loaded,list) else loaded.get('items',[])
        except (ValueError,TypeError): pass
    by_id={x['id']:x for x in existing if isinstance(x,dict) and x.get('id')}
    now=datetime.now(timezone.utc)
    stats={}
    for category,queries in CATEGORIES.items():
        count=0
        for query in queries:
            url='https://news.google.com/rss/search?q='+quote(query+' when:7d')+'&hl=ko&gl=KR&ceid=KR:ko'
            try:
                response=requests.get(url,headers=HEADERS,timeout=20)
                response.raise_for_status()
                feed=feedparser.parse(response.content)
                for entry in feed.entries[:25]:
                    link=entry.get('link','')
                    if not link.startswith('https://'): continue
                    published=date_of(entry)
                    if published and (now-published).days>MAX_DAYS: continue
                    title=clean(entry.get('title',''))
                    if not title: continue
                    uid=hashlib.sha256((category+'|'+link).encode()).hexdigest()[:20]
                    if uid in by_id: continue
                    summary=clean(entry.get('summary',''))[:240]
                    by_id[uid]={'id':uid,'category':category,'title':title,'url':link,
                       'date':(published or now).astimezone(KST).strftime('%Y-%m-%d'),
                       'summary':summary or '원문에서 상세 내용을 확인하세요.',
                       'source':clean(entry.get('source',{}).get('title','')) or 'Google 뉴스 RSS',
                       'collected_at':now.astimezone(KST).isoformat()}
                    count+=1
            except (requests.RequestException,ValueError) as exc:
                print(f'[WARN] {category}: {exc}')
        stats[category]=count
    # Keep recent 90 days, with cap to avoid repository bloat
    cutoff=(now-timedelta(days=90)).astimezone(KST).strftime('%Y-%m-%d')
    items=[x for x in by_id.values() if x.get('date','')>=cutoff]
    items.sort(key=lambda x:(x.get('date',''),x.get('collected_at','')),reverse=True)
    DATA.write_text(json.dumps(items[:1500],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('New:',stats,'Total:',len(items[:1500]))

if __name__=='__main__': main()
