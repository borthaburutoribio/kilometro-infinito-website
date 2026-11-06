"""Baja el contenido de cada pagina de kilometroinfinito (clasificaciones) a raw/pages. No re-baja lo que ya esta."""
import json,urllib.request,time,pathlib
R=pathlib.Path(__file__).parent/'raw'
pg=json.load(open(R/'pages_km.json',encoding='utf8'))
ok=0;err=0
for p in pg:
    f=R/'pages'/f"{p['id']}.json"
    if f.exists(): ok+=1; continue
    u=f"https://www.kilometroinfinito.com.ar/feeds/pages/default/{p['id']}?alt=json"
    for a in range(3):
        try:
            j=json.loads(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=90).read().decode('utf8'))
            json.dump({'t':p['t'],'d':p['d'],'u':p['u'],'c':j['entry']['content']['$t']},open(f,'w',encoding='utf8'),ensure_ascii=False); ok+=1; break
        except Exception as e:
            time.sleep(3)
            if a==2: err+=1; print('ERR',p['u'],e)
    time.sleep(.25)
print('ok',ok,'err',err)
