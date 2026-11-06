"""Baja el indice de posteos y paginas de los dos Blogger de KMI (solo metadatos de paginas)."""
import json,urllib.request,time,sys,pathlib
R=pathlib.Path(__file__).parent/'raw'
UA={'User-Agent':'Mozilla/5.0'}
def get(u):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=120).read().decode('utf8'))
for d,k in [('www.kilometroinfinito.com.ar','km'),('www.kmitodoapulmon.com.ar','pul')]:
    out=[];i=1
    while True:
        j=get(f'https://{d}/feeds/posts/default?alt=json&max-results=150&start-index={i}')
        e=j['feed'].get('entry',[]); out+=e
        if len(e)<1: break
        i+=len(e); time.sleep(.3)
    json.dump(out,open(R/f'posts_{k}.json','w',encoding='utf8'),ensure_ascii=False)
    pg=[];i=1
    while True:
        j=get(f'https://{d}/feeds/pages/summary?alt=json&max-results=150&start-index={i}')
        e=j['feed'].get('entry',[])
        if not e: break
        pg+=[{'t':x['title']['$t'],'d':x['published']['$t'][:10],'id':x['id']['$t'].split('page-')[-1],'u':[l['href'] for l in x['link'] if l['rel']=='alternate'][0]} for x in e]
        i+=len(e); time.sleep(.3)
    json.dump(pg,open(R/f'pages_{k}.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
    print(d,'posts',len(out),'pages',len(pg))
