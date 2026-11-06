import json,re,html,sys,pathlib
sys.stdout.reconfigure(encoding='utf-8')
R=pathlib.Path(__file__).parent/'raw'
po=json.load(open(R/'posts_km.json',encoding='utf8'))
def tx(c):
    t=html.unescape(re.sub('<(style|script)[^>]*>.*?</\1>','',c,flags=re.S)); t=re.sub(r'<(br|/p|/div|/tr|/li)[^>]*>','\n',t); t=re.sub('<[^>]+>',' ',t); t=re.sub(r'[ \t\xa0]+',' ',t); return re.sub(r'\n\s*\n+','\n',t).strip()
for e in po:
    tt=e['title']['$t']
    if tt.startswith('Un poco de Historia') or 'REGLAMENTOS Y PUNT' in tt or 'Se fue la Revancha' in tt:
        print('=====',e['published']['$t'][:10],tt); print(tx(e['content']['$t'])[:3500])
long=sorted(po,key=lambda e:-len(tx(e['content']['$t'])))[:25]
print('LONGEST'); [print(e['published']['$t'][:10],e['title']['$t'][:70],len(tx(e['content']['$t']))) for e in long]
imgs=[re.findall(r'<img[^>]+src="([^"]+)"',e['content']['$t']) for e in po]
print('with imgs',sum(1 for i in imgs if i),'total',sum(len(i) for i in imgs))
