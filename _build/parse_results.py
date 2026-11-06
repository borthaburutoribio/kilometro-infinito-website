"""Convierte las 462 paginas de Blogger y los posteos de clasificaciones en datos.

Salida en _build/data/:
  races.json   lista de carreras (slug, nombre, fecha, lugar, disciplina, urls viejas, cantidad)
  results/     una tabla por pagina vieja: {title, date, oldUrl, sections:[{name, cols, rows}]}
No inventa nada: si una fila no se puede leer, se descarta y se cuenta.
"""
import json, re, html, glob, pathlib, sys, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')
B = pathlib.Path(__file__).parent
OUT = B / 'data' / 'results'
OUT.mkdir(parents=True, exist_ok=True)

STRIP = re.compile(r'<(style|script|xml)[^>]*>.*?</\1>|<!--.*?-->', re.S | re.I)
TR = re.compile(r'<tr[^>]*>(.*?)</tr>', re.S | re.I)
TD = re.compile(r'<t[dh]([^>]*)>(.*?)</t[dh]>', re.S | re.I)
TAG = re.compile(r'<[^>]+>')


def clean(x):
    x = html.unescape(TAG.sub(' ', x)).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', x).strip()


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


TIME = re.compile(r'^\d{1,2}:\d{2}(:\d{2})?([.,]\d+)?$')
NAME_H = ('CORREDOR', 'APELLIDO', 'NOMBRE', 'ATLETA', 'COMPETIDOR', 'PARTICIPANTE', 'PAREJA', 'EQUIPO', 'CICLISTA')


def col_kind(h):
    h = h.upper().strip()
    if any(k in h for k in NAME_H):
        return 'name'
    if h.startswith(('VTA', 'VUELTA', 'V.', 'PC', 'PARCIAL', 'RUN', 'BIKE', 'MTB', 'PIE', 'TRANS', 'T1', 'T2')):
        return 'split'
    if 'TIEMPO' in h or h in ('TOTAL', 'NETO', 'TIEMPO NETO'):
        return 'time'
    if 'PROCED' in h or 'LOCALIDAD' in h or 'CIUDAD' in h or 'ORIGEN' in h:
        return 'from'
    if 'PLACA' in h or 'DORSAL' in h or h in ('NRO', 'Nº', 'N°', 'NUM', 'NÚMERO'):
        return 'bib'
    if 'CATEG' in h or h in ('CAT', 'CAT.'):
        return 'cat'
    if 'DIF' in h:
        return 'gap'
    if 'PROM' in h:
        return 'avg'
    if 'GRAL' in h or 'GENERAL' in h:
        return 'posg'
    if h.startswith('POS') or h in ('PUESTO', 'LUGAR', 'ORDEN', '#'):
        return 'pos'
    if 'REPRESENTA' in h or 'EQUIPO' in h:
        return 'team'
    return 'x'


def parse_page(raw):
    """Devuelve secciones [{name, rows:[{pos,posg,name,bib,from,time,cat,gap,avg,splits}]}]."""
    c = STRIP.sub('', raw)
    rows = []
    for tr in TR.findall(c):
        cells = []
        for attrs, inner in TD.findall(tr):
            m = re.search(r'colspan="?(\d+)', attrs, re.I)
            cells.append((clean(inner), int(m.group(1)) if m else 1))
        if cells:
            rows.append(cells)
    sections, cur, kinds, label, dropped = [], None, None, '', 0
    for cells in rows:
        vals = [v for v, _ in cells]
        up = [v.upper() for v in vals]
        filled = [v for v in vals if v]
        # encabezado: tiene una columna de nombre y otra de posicion o tiempo
        ks = [col_kind(v) if v else 'x' for v in vals]
        if 'name' in ks and ('pos' in ks or 'time' in ks or 'posg' in ks) and not any(TIME.match(v) for v in vals):
            kinds = []
            for (v, span), k in zip(cells, ks):
                kinds += [k] + ['x'] * (span - 1)
            cur = {'name': label, 'rows': []}
            sections.append(cur)
            label = ''
            continue
        # etiqueta de categoria: una sola celda con texto
        if len(filled) == 1 and not TIME.match(filled[0]) and len(filled[0]) < 90:
            label = filled[0]
            continue
        if not kinds or cur is None:
            continue
        expanded = []
        for v, span in cells:
            expanded += [v] + [''] * (span - 1)
        rec = {'splits': []}
        for k, v in zip(kinds, expanded):
            if not v:
                continue
            if k == 'split':
                rec['splits'].append(v)
            elif k in ('pos', 'posg', 'name', 'bib', 'from', 'time', 'cat', 'gap', 'avg', 'team') and k not in rec:
                rec[k] = v
        if not rec.get('name') or len(rec['name']) < 3 or not re.search('[A-Za-zÁÉÍÓÚÑáéíóúñ]', rec['name']):
            dropped += 1
            continue
        if not rec.get('time') and not rec.get('pos'):
            dropped += 1
            continue
        if not rec['splits']:
            del rec['splits']
        cur['rows'].append(rec)
    sections = [s for s in sections if s['rows']]
    return sections, dropped


posts = json.load(open(B / 'raw' / 'posts_km.json', encoding='utf8'))
url2post = {}
for e in posts:
    for u in re.findall(r'href="([^"]+)"', e['content']['$t']):
        u = html.unescape(u).split('?')[0].replace('http://', 'https://')
        if '/p/' in u:
            url2post.setdefault(u.split('/p/')[-1].split('#')[0], e)

pages, stats = [], collections.Counter()
for f in sorted(glob.glob(str(B / 'raw' / 'pages' / '*.json'))):
    p = json.load(open(f, encoding='utf8'))
    slug = p['u'].split('/p/')[-1].replace('.html', '')
    secs, dropped = parse_page(p['c'])
    n = sum(len(s['rows']) for s in secs)
    stats['dropped'] += dropped
    if n < 3:
        stats['sin_tabla'] += 1
        pages.append({'slug': slug, 'title': p['t'], 'date': p['d'], 'n': 0, 'kind': 'texto'})
        continue
    title = re.sub(r'\s+', ' ', p['t']).strip()
    json.dump({'slug': slug, 'title': title, 'date': p['d'], 'oldUrl': p['u'], 'sections': secs},
              open(OUT / f'{slug}.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    stats['tablas'] += 1
    stats['filas'] += n
    pages.append({'slug': slug, 'title': title, 'date': p['d'], 'n': n, 'kind': 'tabla', 'secs': len(secs)})

json.dump(pages, open(B / 'data' / 'pages_index.json', 'w', encoding='utf8'), ensure_ascii=False, indent=0)
print(dict(stats))
tab = [p for p in pages if p['kind'] == 'tabla']
print('por anio', sorted(collections.Counter(p['date'][:4] for p in tab).items()))
print('sin tabla', [p['title'][:50] for p in pages if p['kind'] != 'tabla'][:25])
s = json.load(open(OUT / f"{tab[-1]['slug']}.json", encoding='utf8'))
print(s['title'], [x['name'] for x in s['sections']][:8], s['sections'][0]['rows'][:2])
s = json.load(open(OUT / f"{tab[0]['slug']}.json", encoding='utf8'))
print(s['title'], [x['name'] for x in s['sections']][:8], s['sections'][0]['rows'][:2])
