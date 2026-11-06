"""Baja la imagen mas grande de cada posteo de IG desde /embed/ (sin login) a raw/ig. Uso: python fetch_ig.py codigos..."""
import re,sys,urllib.request,pathlib,html,time,json
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36'}
R=pathlib.Path('raw/ig'); caps={}
capf=pathlib.Path('raw/ig_caps.json')
if capf.exists(): caps=json.load(open(capf,encoding='utf8'))
for a in sys.argv[1:]:
    k,c=a[0],a[1:]; f=R/f'{c}.jpg'
    if f.exists(): continue
    path='p' if k=='p' else 'reel'
    try:
        h=urllib.request.urlopen(urllib.request.Request(f'https://www.instagram.com/{path}/{c}/embed/captioned/',headers=UA),timeout=30).read().decode('utf8','ignore')
    except Exception as e: print('ERR',c,str(e)[:50]); continue
    best=None;bw=0
    for m in re.finditer(r'srcset="([^"]+)"',h):
        for part in html.unescape(m.group(1)).split(','):
            s=part.strip().split(' ')
            if len(s)==2 and s[1].endswith('w') and int(s[1][:-1])>bw: bw=int(s[1][:-1]);best=s[0]
    if not best:
        m=re.search(r'class="EmbeddedMediaImage"[^>]+src="([^"]+)"',h)
        if m: best=html.unescape(m.group(1))
    cap=re.search(r'class="Caption"[^>]*>(.*?)<div class="CaptionComments',h,flags=re.S)
    if cap: caps[c]=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',cap.group(1)))).strip()[:300]
    if not best: print('noimg',c); continue
    try: f.write_bytes(urllib.request.urlopen(urllib.request.Request(best,headers=UA),timeout=30).read()); print(c,bw)
    except Exception as e: print('ERRimg',c,str(e)[:50])
    time.sleep(.6)
json.dump(caps,open(capf,'w',encoding='utf8'),ensure_ascii=False,indent=0)
