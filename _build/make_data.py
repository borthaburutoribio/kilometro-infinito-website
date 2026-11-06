"""Une posteos + paginas de resultados en eventos, series e indice de corredores.
Lee data/results/*.json y raw/posts_km.json. Escribe data/events.json, data/series.json y ../assets/data/*.
Todos los numeros salen de contar lo que Adrian ya publico: nada se estima."""
import json, re, html, glob, pathlib, sys, unicodedata, collections, zlib, datetime
sys.stdout.reconfigure(encoding='utf-8')
B = pathlib.Path(__file__).parent
D = B / 'data'
SITE = B.parent
(SITE / 'assets' / 'data' / 'r').mkdir(parents=True, exist_ok=True)

MES = {'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'sep': 9, 'set': 9, 'oct': 10, 'nov': 11, 'dic': 12}


def norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', re.sub(r"[^a-z0-9 /]", ' ', s)).strip()


def date_from(title, fallback):
    t = norm(title)
    t2 = title
    m = re.search(r'(\d{1,2})\s*[/\-.]\s*(\d{1,2})\s*[/\-.]\s*(20\d{2}|\d{2})\b', t2)
    if m:
        d, mo, y = int(m[1]), int(m[2]), int(m[3])
    else:
        m = re.search(r'(\d{1,2})\s*(?:de\s*|[/\- ]\s*)?(ene|feb|mar|abr|may|jun|jul|ago|sep|set|oct|nov|dic)[a-z]*\s*(?:de\s*|[/\- ]\s*)?(20\d{2}|\d{2})\b', t)
        if not m:
            return fallback
        d, mo, y = int(m[1]), MES[m[2]], int(m[3])
    y = y + 2000 if y < 100 else y
    try:
        dt = datetime.date(y, mo, d)
    except ValueError:
        return fallback
    fb = datetime.date.fromisoformat(fallback)
    # un titulo con un error de tipeo (204 por 2024) no debe mover la carrera de anio
    return dt.isoformat() if abs((dt - fb).days) < 400 else fallback


def clean_title(t):
    t = html.unescape(t).replace('\xa0', ' ')
    t = re.sub(r'[“”"«»]', '', t)
    t = re.sub(r'\b\d{1,2}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*(20\d{2}|\d{2,3})\b', ' ', t)
    t = re.sub(r'\b\d{1,2}\s*(de\s*|[/\- ]\s*)?(ene|feb|mar|abr|may|jun|jul|ago|sep|set|oct|nov|dic)[a-záéíóú]*\.?\s*(de\s*|[/\- ]\s*)?(20\d{2}|\d{2})?\b', ' ', t, flags=re.I)
    t = re.sub(r'\b(clasificaci[oó]n(es)?|clasifcaciones|clasifiacion|resultados|comentario y|comentario|y clasificaci[oó]n|por categor[ií]as|generale?s?|general|categor[ií]as|con diferencias y p\w*|final)\b', ' ', t, flags=re.I)
    t = re.sub(r'\b(de|del|y)\s*(?=[-/–—]|$)', ' ', t, flags=re.I)
    t = re.sub(r'\s*(--+|//+|[-–—/]+)\s*', ' · ', t)
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'(\s*·\s*)+', ' · ', t).strip(' ·-')
    return t


LOWER = {'de', 'del', 'la', 'las', 'los', 'a', 'al', 'y', 'en', 'el', 'por', 'con'}
UP = {'MTB', 'KMI', 'XCO', 'XCC', 'CRI', 'TDO', 'ACEPT', 'RB', 'MDQ', 'MDP', 'FDT', 'II', 'III', 'IV', 'BTT'}


def smart(t):
    out = []
    for i, w in enumerate(t.split(' ')):
        u = w.upper().strip('.,()')
        if u in UP:
            out.append(u)
        elif w.lower() in LOWER and i:
            out.append(w.lower())
        elif re.match(r'^\d', w):
            out.append(w.lower())
        else:
            out.append(w[:1].upper() + w[1:].lower())
    return ' '.join(out)


PLACES = [('Mar de las Pampas', 'mar de las pampas', -37.327, -57.023), ('Mar de Cobo', 'mar de cobo|mar de coco', -37.77, -57.45),
          ('Mar Chiquita', 'mar chiquita', -37.746, -57.426), ('Vivoratá', 'vivorata', -37.664, -57.667), ('Coronel Vidal', 'vidal', -37.446, -57.729),
          ('Mechongué', 'mechongue', -38.15, -58.22), ('Batán', 'batan', -38.006, -57.71), ('Azucena', 'azucena', -37.52, -59.33),
          ('Gardey', 'gardey', -37.283, -59.363), ('Sierra de los Padres', 'sierras? de los padres|7 lomas|siete lomas|laguna de los padres', -37.948, -57.783),
          ('Mar del Plata', 'mar del plata|mdp|mdq|mar y sierras|difuntos|feliz', -38.002, -57.556), ('Tandil', 'tandil|escuela granja|cerro leones|noel bike', -37.326, -59.135),
          ('Barker', 'barker|villa cacique', -37.643, -59.391), ('Balcarce', 'balcarce|leones|3 ?hs|tres horas|3 horas|escuela nro 16|escuela 16|sudamericano|juveniles', -37.846, -58.255),
          ('Ayacucho', 'ayacucho|tres cruces|temple de acero|kmi mtb timing|fdt|caminos de luna', -37.151, -58.488), ('Rauch', 'rauch|hangar', -36.774, -59.089),
          ('Miramar', 'miramar', -38.27, -57.84), ('Villa Gesell', 'gesell|macedo|dua de fuego', -37.263, -56.973), ('Pinamar', 'pinamar', -37.108, -56.861),
          ('Costa del Este', 'costa del este', -36.606, -56.682), ('General Lavalle', 'lavalle|podazza|fiestas mayas', -36.41, -56.942), ('Quequén', 'quequen|costa brava', -38.566, -58.711),
          ('Necochea', 'necochea|senderos', -38.555, -58.74), ('Maipú', 'maipu', -36.866, -57.878), ('Olavarría', 'olavarria|sierras bayas', -36.89, -60.322),
          ('Pila', 'pila', -36.0, -58.14), ('Las Flores', 'las flores|ciudad de las flores', -36.014, -59.1), ('Castelli', 'castelli|la rosita', -36.09, -57.81),
          ('Lezama', 'lezama', -35.87, -57.9), ('Garibaldi', 'garibaldi', -36.5, -59.5), ('Dolores', 'dolores', -36.31, -57.67), ('Cacharí', 'cachari', -36.378, -59.5)]


FIX = [('Batan', 'Batán'), ('Desafio', 'Desafío'), ('Duatlon', 'Duatlón'), ('Dualton', 'Duatlón'), ('Mechongue', 'Mechongué'), ('Olavarria', 'Olavarría'), ('Maipu', 'Maipú'), ('Quequen', 'Quequén'), ('Vivorata', 'Vivoratá'), ('Dua Cross', 'Dúa Cross'), ('Sebastian', 'Sebastián'), ('Tandileofu', 'Tandileofú'), ('Gesele', 'Gesell'), (' Domingo', ''), ('Coronel Vidal Bike', 'Coronel Vidal')]


def pretty(n):
    parts = [p.strip() for p in n.split(' · ') if p.strip()]
    parts = [p for p in parts if not re.match(r'^(gral\.? y competitivas|categor|general|mar de coco)', p, re.I)]
    n = parts[0] if parts else n
    n = re.sub(r'^(del|de la|de|el)\s+', '', n, flags=re.I)
    n = re.sub(r'\s*\(?(Tandil|Mdp)\)?$', '', n) if len(n) > 18 else n
    for a, b in FIX:
        n = n.replace(a, b)
    return n[:1].upper() + n[1:]


def place_of(t):
    n = norm(t)
    for name, rx, *_ in PLACES:
        if re.search(rf'\b({rx})\b', n):
            return name
    return ''


def discipline(t):
    n = norm(t)
    if 'campeonato' in n and re.search(r'kmi|regional|zonal|final|posiciones', n) and not re.search(r'fecha', n): return 'Campeonato'
    if re.search(r'\bdua|duatl|dualton', n): return 'Duatlón'
    if re.search(r'corre\b|corriendo|maraton|running|pedestre|\d+ ?k\b|fiestas mayas|carrera nocturna', n): return 'Running'
    if re.search(r'mtb|bike|rally|rural|ciclis|vuelta|desafio|endurance|series|contrarreloj|gran premio|lomas', n): return 'MTB y rural bike'
    return 'Otras'


SERIES = [('vuelta-a-gardey', 'Vuelta a Gardey', r'gardey'),
          ('vuelta-escuela-granja', 'Vuelta a la Escuela Granja', r'escuela granja'),
          ('desafio-tres-cruces', 'Desafío de las Tres Cruces', r'tres cruces'),
          ('desafio-de-los-leones', 'Desafío de los Leones', r'desafio de los leones|leones'),
          ('vuelta-coronel-vidal', 'Vuelta a Coronel Vidal', r'vuelta a (coronel|cnel) vidal|vuelta (coronel|cnel) vidal'),
          ('vuelta-mtb-batan', 'Vuelta de MTB Rural a Batán', r'vuelta (de )?(mtb|mtb rural).*batan|batan.*vuelta'),
          ('rally-costa-del-este', 'Rally Costa del Este', r'costa del este'),
          ('rally-cross-miramar', 'Rally Cross Miramar', r'cross miramar'),
          ('rally-mar-y-sierras', 'Rally Mar y Sierras', r'mar y sierras'),
          ('mtb-series-difuntos', 'MTB Series Sierra de los Difuntos', r'difuntos'),
          ('duatlon-mar-chiquita', 'Duatlón Rural Laguna Mar Chiquita', r'(duatlon|dualton).*mar chiquita'),
          ('rural-bike-mechongue', 'Rural Bike Mechongué', r'mechongue'),
          ('rally-solidario-gesell', 'Rally Bike Solidario del Rotary', r'solidario'),
          ('pinamar-bike-race', 'Pinamar Bike Race', r'pinamar'),
          ('siete-lomas', 'Desafío de las 7 Lomas', r'7 lomas|siete lomas'),
          ('tres-horas-balcarce', 'Las 3 Horas de MTB en Balcarce', r'3 ?hs|3 horas|tres horas'),
          ('vuelta-a-pila', 'Vuelta al Pueblo de Pila', r'\bpila\b'),
          ('rural-bike-podazza', 'Rural Bike Sebastián Podazza', r'podazza')]


def series_of(t):
    n = norm(t)
    for sid, _, rx in SERIES:
        if re.search(rx, n):
            return sid
    return None


posts = json.load(open(B / 'raw' / 'posts_km.json', encoding='utf8'))
page_index = {p['slug']: p for p in json.load(open(D / 'pages_index.json', encoding='utf8'))}
flyers = {}
for f in json.load(open(B / 'raw' / 'flyers.json', encoding='utf8')):
    flyers.setdefault((f['d'], f['t']), f['f'])
ok_flyers = {p.name for p in (B / 'raw' / 'flyers').glob('*.jpg')}

events, used = [], set()
for e in sorted(posts, key=lambda x: x['published']['$t']):
    c = e['content']['$t']
    title = e['title']['$t']
    pub = e['published']['$t'][:10]
    url = [l['href'] for l in e['link'] if l['rel'] == 'alternate'][0]
    links = []
    for href, text in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', c, flags=re.S):
        href = html.unescape(href)
        if '/p/' not in href or 'kilometroinfinito' not in href:
            continue
        slug = href.split('/p/')[-1].split('.html')[0]
        if slug in page_index and page_index[slug]['kind'] == 'tabla' and slug not in [l['slug'] for l in links]:
            links.append({'slug': slug})
    fl = flyers.get((pub, title))
    fl = fl if fl in ok_flyers else None
    ev = {'title': title, 'name': pretty(smart(clean_title(title))), 'date': date_from(title, pub), 'pub': pub,
          'post': url.split('kilometroinfinito.com.ar/')[-1], 'flyer': fl, 'pages': [], 'place': place_of(title), 'disc': discipline(title), 'series': series_of(title)}
    for l in links:
        p = page_index[l['slug']]
        used.add(l['slug'])
        low = norm(p['title'])
        kind = 'general' if 'general' in low else 'categorias' if 'categ' in low else ''
        ev['pages'].append({'slug': l['slug'], 'kind': kind, 'n': p['n'], 'title': p['title']})
    # si no se sabe cual es cual: la de mas filas es la general o la unica
    events.append(ev)

# paginas que ningun posteo enlaza: cada una es un evento propio, o se suma a uno del mismo nombre y fecha
for slug, p in page_index.items():
    if p['kind'] != 'tabla' or slug in used:
        continue
    d = date_from(p['title'], p['date'])
    nm = pretty(smart(clean_title(p['title'])))
    hit = next((ev for ev in events if ev['date'] == d and norm(ev['name'])[:14] == norm(nm)[:14]), None)
    low = norm(p['title'])
    kind = 'general' if 'general' in low else 'categorias' if 'categ' in low else ''
    pg = {'slug': slug, 'kind': kind, 'n': p['n'], 'title': p['title']}
    if hit:
        hit['pages'].append(pg)
    else:
        events.append({'title': p['title'], 'name': nm, 'date': d, 'pub': p['date'], 'post': None, 'flyer': None, 'pages': [pg],
                       'place': place_of(p['title']), 'disc': discipline(p['title']), 'series': series_of(p['title'])})

race_events = [ev for ev in events if ev['pages']]
race_events.sort(key=lambda x: x['date'], reverse=True)


def first_row(slug):
    data = json.load(open(D / 'results' / f'{slug}.json', encoding='utf8'))
    for s in data['sections']:
        for r in s['rows']:
            if re.match(r'^1\b', r.get('posg', '') or r.get('pos', '')) and r.get('time'):
                return r
        break
    return None


names = collections.defaultdict(dict)  # clave normalizada -> evento -> registro
display = {}
for i, ev in enumerate(race_events):
    ev['id'] = i
    # participantes: la pagina con mas filas (la general, cuando hay)
    best = max(ev['pages'], key=lambda p: p['n'])
    ev['n'] = best['n']
    gen = next((p for p in ev['pages'] if p['kind'] == 'general'), best)
    w = first_row(gen['slug'])
    if w:
        ev['winner'] = {'name': w['name'], 'time': w['time']}
    # primero categorias (trae el nombre de la categoria), despues completa con el resto
    for p in sorted(ev['pages'], key=lambda x: (0 if x['kind'] == 'categorias' else 1)):
        data = json.load(open(D / 'results' / f"{p['slug']}.json", encoding='utf8'))
        for s in data['sections']:
            for r in s['rows']:
                for one in re.split(r'\s*/\s*', r['name']):
                    k = norm(one)
                    if len(k) < 5 or ' ' not in k:
                        continue
                    display.setdefault(k, ' '.join(w[:1].upper() + w[1:] for w in one.lower().split()))
                    if i not in names[k]:
                        cat = r.get('cat') or s.get('name') or ''
                        names[k][i] = [i, re.sub(r'\s.*', '', r.get('pos', '')), r.get('time', ''), cat[:32], p['slug']]

# Indice para la busqueda en el navegador
keys = sorted(names, key=lambda k: (-len(names[k]), k))
shards = collections.defaultdict(dict)
for k in keys:
    shards[zlib.crc32(k.encode()) % 96][k] = sorted(names[k].values(), key=lambda r: race_events[r[0]]['date'], reverse=True)
json.dump([[display[k], len(names[k])] for k in keys], open(SITE / 'assets/data/names.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
for n, v in shards.items():
    json.dump(v, open(SITE / f'assets/data/r/{n}.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
json.dump([[e['name'], e['date'], e['place'], e['disc']] for e in race_events], open(SITE / 'assets/data/races.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))

# Series y lugares
series = {}
for sid, name, _ in SERIES:
    eds = [e for e in race_events if e['series'] == sid]
    if eds:
        series[sid] = {'id': sid, 'name': name, 'editions': [e['id'] for e in eds], 'place': collections.Counter(e['place'] for e in eds).most_common(1)[0][0], 'total': sum(e['n'] for e in eds)}
places = collections.Counter(e['place'] for e in race_events if e['place'])
geo = {n: (la, lo) for n, _, la, lo in PLACES}
stats = {'events': len(race_events), 'rows_published': sum(p['n'] for e in race_events for p in e['pages']), 'results_unique': sum(len(v) for v in names.values()), 'runners': len(keys),
         'first_year': int(min(e['date'] for e in race_events)[:4]), 'places': len(places), 'by_year': sorted(collections.Counter(e['date'][:4] for e in race_events).items()),
         'by_disc': collections.Counter(e['disc'] for e in race_events).most_common()}
json.dump(race_events, open(D / 'events.json', 'w', encoding='utf8'), ensure_ascii=False, indent=0)
json.dump(series, open(D / 'series.json', 'w', encoding='utf8'), ensure_ascii=False, indent=0)
json.dump({'stats': stats, 'places': [[n, c, *geo[n]] for n, c in places.most_common()]}, open(D / 'stats.json', 'w', encoding='utf8'), ensure_ascii=False, indent=0)

same = sum(1 for e in race_events if e['pub'] == e['date'] and e['disc'] != 'Campeonato')
nextd = sum(1 for e in race_events if e['pub'] != e['date'] and e['post'] and abs((datetime.date.fromisoformat(e['pub']) - datetime.date.fromisoformat(e['date'])).days) <= 2)
print('publicadas mismo dia', same, 'en 2 dias', nextd, 'de', len(race_events))
print(stats)
print('places', places.most_common(40))
print('series', [(s['name'], len(s['editions']), s['place']) for s in series.values()])
print('sin lugar', sum(1 for e in race_events if not e['place']), [e['name'][:50] for e in race_events if not e['place']][:15])
for e in race_events[:8]:
    print(e['date'], e['name'], '|', e['place'], '|', e['disc'], '|', e['n'], '|', [p['kind'] for p in e['pages']], e.get('winner'))
k = keys[0]
print('mas carreras', display[k], len(names[k]), [display[x] for x in keys[1:6]], [len(names[x]) for x in keys[1:6]])
