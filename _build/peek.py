import json,re,html,sys,collections,pathlib
sys.stdout.reconfigure(encoding='utf-8')
R=pathlib.Path(__file__).parent/'raw'
pg=json.load(open(R/'pages_km.json',encoding='utf8')); pp=json.load(open(R/'pages_pul.json',encoding='utf8'))
print(sorted(collections.Counter(p['d'][:4] for p in pg).items()))
print('PUL pages:'); [print(p['d'],p['t'][:90],p['u'].split('/')[-1]) for p in pp]
po=json.load(open(R/'posts_km.json',encoding='utf8'));print('posts km',len(po),sorted(collections.Counter(e['published']['$t'][:4] for e in po).items()))
pu=json.load(open(R/'posts_pul.json',encoding='utf8'));print('posts pul',len(pu))
for e in pu[:40]: print(e['published']['$t'][:10],e['title']['$t'][:80])
print('oldest km:');[print(e['published']['$t'][:10],e['title']['$t'][:80]) for e in po[-12:]]
