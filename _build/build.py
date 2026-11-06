"""Genera todo el sitio de Kilómetro Infinito. Correr: python _build/build.py
Mantiene las URLs viejas de los dos Blogger (/p/*.html y /AAAA/MM/*.html) para no perder lo que Google ya conoce."""
import json, re, html, glob, pathlib, sys, shutil, datetime, collections, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
B = pathlib.Path(__file__).parent
SITE = B.parent
D = B / 'data'
NOINDEX = True          # muestra: al lanzar con el dominio real, poner False
DOMAIN = 'https://www.kilometroinfinito.com.ar'
V = "9"
WA = '5492494551251'    # (0249) 15-455-1251, A CONFIRMAR que tenga WhatsApp
FORM = 'https://docs.google.com/forms/d/e/1FAIpQLSegLqTnWHF24_hhah0eCGhpEGIKlq71XwLnVv1Ek3I0skuifA/viewform'
MAIL = 'kminfinito@live.com.ar'
IG = 'https://www.instagram.com/kminfinito/'
POS_KMI = 'https://docs.google.com/spreadsheets/d/1h9AeYl0ClRnpHUMTt_7VwpnqsYwFmUZoqhFEcxXVCYs/edit?usp=sharing'
POS_3P = 'https://docs.google.com/spreadsheets/d/1xYnDkZZXhkPNhwY4M6jldYbkFb69C2Qcar6OFJ3lMfA/edit?usp=sharing'

E = json.load(open(D / 'events.json', encoding='utf8'))
SER = json.load(open(D / 'series.json', encoding='utf8'))
ST = json.load(open(D / 'stats.json', encoding='utf8'))
PH = json.load(open(D / 'photos.json', encoding='utf8'))
S = ST['stats']
ev_by_slug = {p['slug']: e for e in E for p in e['pages']}
esc = lambda x: html.escape(str(x), quote=True)
MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']


def fdate(s, year=True):
    d = datetime.date.fromisoformat(s)
    return f'{d.day} de {MES[d.month - 1]}' + (f' de {d.year}' if year else '')


def miles(n):
    return f'{n:,}'.replace(',', '.')


def img(name, cls='', sizes='', lazy=True, attrs=''):
    p = PH[name]
    return f'<img src="{{{{R}}}}assets/img/{name}.webp" width="{p["w"]}" height="{p["h"]}" alt="{esc(p["alt"])}"' + (' loading="lazy" decoding="async"' if lazy else '') + (f' class="{cls}"' if cls else '') + (f' {attrs}' if attrs else '') + '>'


def flyer(fname, alt, cls='', lazy=True):
    if not fname:
        return ''
    base = fname[:-4]
    if not (SITE / 'assets' / 'afiches' / f'{base}.webp').exists():
        return ''
    return f'<img src="{{{{R}}}}assets/afiches/{base}.webp" alt="Afiche de {esc(alt)}"' + (' loading="lazy" decoding="async"' if lazy else '') + (f' class="{cls}"' if cls else '') + '>'


NAV = [('Calendario', 'calendario/'), ('Resultados', 'resultados/'), ('Competencias', 'competencias/'), ('Campeonatos', 'campeonatos/'), ('Cronometraje', 'cronometraje/'), ('Historia', 'historia/'), ('Fotos', 'fotos/')]
written = []


def page(path, title, desc, body, active='', schema=None, noindex=False, sitemap=True, fab=True, canonical=True, band=None):
    """path sin barra inicial: 'calendario/index.html' o 'p/x.html'."""
    hero_list = ['arco-bienvenidos-rojo-ciclistas', 'largada-mtb-arco-negro-peloton', 'ciclista-barro-arco-negro', 'corredores-reunidos-previa', 'largada-running-arco-rojo', 'ciclista-barro-bosque', 'podio-running-mar-de-cobo']
    pic = band or hero_list[sum(map(ord, path)) % len(hero_list)]
    body = body.replace('<section class="ph">', '<section class="ph">' + img(pic, 'ph-bg', lazy=False), 1)
    depth = path.count('/')
    R = '../' * depth or './'
    url = '/' + path.replace('index.html', '')
    nav = ''.join(f'<a href="{R}{u}"' + (' aria-current="page"' if u == active else '') + f'>{n}</a>' for n, u in NAV)
    sc = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (schema or []))
    robots = '<meta name="robots" content="noindex,follow">' if (NOINDEX or noindex) else ''
    cta = f'<a class="btn y fab" href="{R}calendario/">Ver carreras e inscribirme</a>' if fab else ''
    doc = f'''<!doctype html>
<html lang="es-AR" data-root="{R}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<link rel="canonical" href="{DOMAIN}{url}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="website"><meta property="og:locale" content="es_AR">
<meta property="og:image" content="{DOMAIN}/assets/img/largada-running-arco-rojo.webp"><meta name="theme-color" content="#0B1533">
<link rel="icon" href="{R}assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{R}assets/kmi.css?v={V}">{sc}
</head>
<body>
<a class="skip" href="#main">Saltar al contenido</a>
<header class="bar"><div class="wrap">
<a class="brand" href="{R}"><img src="{R}assets/img/logo-kmi.webp" width="44" height="44" alt="">Kilómetro Infinito</a>
<button class="menu-t" aria-expanded="false">Menú</button>
<nav class="nav" aria-label="Principal">{nav}<a class="btn" href="{R}contacto/">Contacto</a></nav>
</div></header>
<main id="main">
{body.replace('{{R}}', R)}
</main>
<footer><div class="wrap foot-m on-ink">
<div><a class="brand" href="{R}"><img src="{R}assets/img/logo-kmi.webp" width="58" height="58" alt="">Kilómetro Infinito</a><p>Cronometraje, clasificación y locución de carreras. Ayacucho, provincia de Buenos Aires. “Único límite, tu imaginación”.</p></div>
<ul>{''.join(f'<li><a href="{R}{u}">{n}</a></li>' for n, u in NAV)}<li><a href="{R}inscripcion/">Cómo inscribirme</a></li><li><a href="{R}contacto/">Contacto</a></li><li><a href="{IG}" rel="noopener">Instagram</a></li><li><a href="mailto:{MAIL}">{MAIL}</a></li></ul>
</div><p class="wrap credit">Sitio hecho por <a href="https://tranqueraweb.com.ar" rel="noopener">Tranquera Digital</a>.</p></footer>
{cta}
<script src="{R}assets/script.js?v={V}" defer></script>
</body></html>'''
    f = SITE / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(doc, encoding='utf8')
    if sitemap:
        written.append(url)


def finder(pid='home', on_ink=True, label='Escribí tu nombre o apellido'):
    return f'''<form class="finder" data-finder role="search" autocomplete="off">
<label for="f-{pid}">{label}</label>
<input id="f-{pid}" type="search" placeholder="Ej: Torres Alberto" autocomplete="off" enterkeyhint="search">
<ul class="sug" aria-live="polite"></ul>
</form>'''


FAQ = [
 ('¿Cómo me inscribo en una carrera?', 'Entrás a la carrera en el calendario, completás la preinscripción y te respondemos por mail con la confirmación y el número de cuenta. Pagás, nos mandás el comprobante y recién ahí quedás anotado. Si no nos llega el comprobante por mail, no estás anotado.'),
 ('¿Cuánto tardan en responder?', 'La respuesta no es automática: contestamos de lunes a viernes, a las 13 y a las 20. Por lo general no pasan más de 24 horas. Revisá la carpeta de spam o no deseado antes de escribirnos de nuevo.'),
 ('¿Puedo anotarme por WhatsApp o por redes?', 'Hoy no tomamos inscripciones por redes ni por WhatsApp. Usá el formulario, o anotate en persona en Bikes Amigorena (Colón 7199, Mar del Plata) o con nosotros en las carreras previas.'),
 ('¿En qué categoría corro?', 'Se inscribe por año de nacimiento: se toma la edad que vas a tener al 31 de diciembre. En la página de cada carrera ponés tu año y te dice tu categoría y cuánto pagás hoy.'),
 ('Me anoté y no puedo ir. ¿Me devuelven la plata?', 'Lo que dice el reglamento de Caminos de Luna: lo abonado no se devuelve, pero se puede transferir a otra persona hasta el 4 de diciembre. Cada sede fija su regla, así que fijate en la página de tu carrera.'),
 ('¿Cuándo salen los resultados?', 'En general el mismo día de la carrera, acá en la web. Por categoría y por general. Con tu nombre también encontrás todas tus carreras anteriores.'),
 ('Quiero cronometrar mi carrera. ¿Qué hago?', 'Contanos fecha, lugar y cuántos corredores esperás, y te pasamos un presupuesto. Vas a Cronometraje, completás cuatro datos y nos llega por WhatsApp.'),
]


def faq_schema(items):
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in items]}


ORG = {'@context': 'https://schema.org', '@type': 'SportsOrganization', 'name': 'Kilómetro Infinito', 'alternateName': 'KMI', 'url': DOMAIN, 'email': MAIL, 'telephone': '+54 249 455-1251', 'slogan': 'Único límite, tu imaginación', 'foundingDate': '2006', 'sameAs': [IG],
       'address': {'@type': 'PostalAddress', 'addressLocality': 'Ayacucho', 'addressRegion': 'Buenos Aires', 'addressCountry': 'AR'}, 'knowsAbout': ['Cronometraje deportivo', 'Mountain bike', 'Rural bike', 'Duatlón', 'Running']}

# ---------------------------------------------------------------- Próximas carreras
CAB_COMP = [['Elite', 18, 34], ['Master A', 35, 39], ['Master B1', 40, 44], ['Master B2', 45, 49], ['Master C1', 50, 54], ['Master C2', 55, 59], ['Master D1', 60, 64], ['Master D2', 65, 200]]
DAM_COMP = [['Damas A', 0, 39], ['Damas B', 40, 49], ['Damas C', 50, 200]]
RACES = [
 {'id': 'rural-bike-mechongue-2026', 'old': '6-rural-bike-mechongue-08-noviembre', 'name': '6º Rural Bike Mechongué', 'date': '2026-11-08', 'start': '2026-11-08T08:30:00-03:00', 'flyer': '2026-11-03_000.jpg',
  'place': 'Mechongué', 'venue': 'Plaza Carmelo Pepi, calle 1 entre 2 y 4', 'org': 'Asociación del Centro Educativo para la Producción Total N° 20, a total beneficio del centro', 'mode': 'Rural bike', 'status': 'Inscripción cerrada: estamos viendo si hay cupos nuevos', 'open': False,
  'sched': [('8.30 hs', 'Acreditación')], 'dist': {'comp': '48 km', 'promo': '32 km', 'prin': '16 km'}, 'champ': 'Anteúltima fecha del 17° Campeonato KMI', 'incl': 'Medalla finisher para todos, kit del corredor, seguro y servicio de cantina.',
  'insc': 'https://docs.google.com/spreadsheets/d/1nuTqwbSyVvKa_WkzPPh1Cq1m7bR_6Qp15irRmW84af8/edit?gid=0#gid=0', 'tiers': [], 'cats': {}, 'info': ''},
 {'id': 'vuelta-coronel-vidal-2026', 'old': 'rural-bike-10va-vuelta-coronel-vidal', 'name': '10ª Vuelta a Coronel Vidal', 'date': '2026-11-22', 'start': '2026-11-22T11:00:00-03:00', 'flyer': '2026-11-02_001.jpg',
  'place': 'Coronel Vidal', 'venue': 'Esc. de Educ. Sec. Agraria N° 1 “Nicanor Ezeyza”, Ruta 55 a 6 km de Ruta 2', 'map': 'https://maps.app.goo.gl/WsZnd6WXckutcfvc6', 'org': '', 'mode': 'Rally bike', 'status': 'Inscripción abierta hasta el 19 de noviembre o hasta completar el cupo', 'open': True,
  'sched': [('8.30 a 10 hs', 'Acreditación en el predio de la Escuela Agraria'), ('11 hs', 'Largadas por categorías')], 'dist': {'comp': '55 km, 5 vueltas', 'promo': '33 km, 3 vueltas', 'prin': '11 km, 1 vuelta'}, 'champ': 'Final del 17° Campeonato KMI “Copa Bikes Amigorena”',
  'incl': 'Kit del corredor, medalla finisher, asistencia sanitaria, derecho a participar, clasificación y sorteos de sponsors. Hay cantina.', 'prizes': '1º al 5º en todas las categorías. 1º al 3º en ambas generales competitivas. Al terminar se entregan los premios del campeonato, del 1º al 3º de cada categoría.',
  'insc': 'https://docs.google.com/spreadsheets/d/1J_fqNHW98RiufZVscVLBkjW3DuuoN4Y32w_XckDLf6g/edit?usp=sharing', 'info': '223 456-7368 (Fernando)', 'infoTel': '+542234567368',
  'tiers': [{'from': '2026-10-09', 'to': '2026-10-23', 'comp': 45000, 'promo': 45000, 'prin': 35000}, {'from': '2026-10-24', 'to': '2026-11-13', 'comp': 55000, 'promo': 55000, 'prin': 45000}, {'from': '2026-11-14', 'to': '2026-11-19', 'comp': 65000, 'promo': 65000, 'prin': 55000}],
  'cats': {'comp': {'d': DAM_COMP, 'c': CAB_COMP}, 'promo': {'d': [['Promo Damas A', 0, 39], ['Promo Damas B', 40, 49], ['Promo Damas C', 50, 200]], 'c': [['Promo Caballeros A', 0, 39], ['Promo Caballeros B', 40, 49], ['Promo Caballeros C', 50, 59], ['Promo Caballeros D', 60, 200]]},
           'prin': {'d': [['Damas Principiantes A', 0, 44], ['Damas Principiantes B', 45, 200]], 'c': [['Caballeros Principiantes A', 0, 44], ['Caballeros Principiantes B', 45, 200]]}}},
 {'id': 'caminos-de-luna-2026', 'old': 'caminos-de-luna-sabado-12-de-diciembre', 'name': 'Caminos de Luna', 'date': '2026-12-12', 'start': '2026-12-12T20:30:00-03:00', 'flyer': '2026-11-01_002.jpg',
  'place': 'Ayacucho', 'venue': 'Cicles Club Ayacucho, Moreno esquina Arenales', 'map': 'https://maps.app.goo.gl/GJ5sBAbbQz1abSqG6', 'org': 'Cicles Club Ayacucho', 'mode': '1° Rural Bike Nocturno, contrarreloj individual', 'status': 'Inscripción abierta hasta el 10 de diciembre', 'open': True,
  'sched': [('18 a 20 hs', 'Acreditación'), ('20.30 hs', 'Inicio de la competencia'), ('22.30 hs aprox.', 'Premiación')], 'dist': {'comp': '45 km, 1 vuelta', 'promo': '45 km, 1 vuelta'}, 'champ': '',
  'incl': 'Kit del corredor, seguro, placa, asistencia sanitaria y clasificación. Hay cantina.', 'prizes': '1º al 5º en todas las categorías. 1º al 3º en ambas generales competitivas.', 'refund': 'Lo abonado no se devuelve si decidís no correr, pero podés transferirlo a otra persona hasta el 4 de diciembre.',
  'insc': '', 'info': '2296-406020 (Ricardo)', 'infoTel': '+542296406020',
  'tiers': [{'from': '2026-10-01', 'to': '2026-10-30', 'comp': 45000, 'promo': 40000}, {'from': '2026-10-31', 'to': '2026-11-27', 'comp': 55000, 'promo': 50000}, {'from': '2026-11-28', 'to': '2026-12-10', 'comp': 70000, 'promo': 65000}],
  'cats': {'comp': {'d': DAM_COMP, 'c': CAB_COMP[:6] + [['Master D', 60, 200]]}, 'promo': {'d': [['Promo Damas A', 0, 39], ['Promo Damas B', 40, 200]], 'c': [['Promo Caballeros A', 0, 39], ['Promo Caballeros B', 40, 54], ['Promo Caballeros C', 55, 200]]}}},
 {'id': 'vuelta-mtb-batan-2027', 'name': '9ª Vuelta de MTB Rural a Batán', 'date': '2027-03-07', 'start': '2027-03-07T09:00:00-03:00', 'flyer': '2026-03-01_023.jpg', 'place': 'Batán', 'mode': 'MTB rural', 'status': 'Fecha confirmada, todavía no publicamos la información de esta edición', 'open': False, 'tiers': [], 'cats': {}, 'sched': [], 'dist': {}, 'champ': '', 'incl': '', 'insc': '', 'venue': '', 'org': '', 'info': '', 'series': 'vuelta-mtb-batan'},
 {'id': 'vuelta-escuela-granja-2027', 'name': '21ª Vuelta a la Escuela Granja', 'date': '2027-03-21', 'start': '2027-03-21T09:00:00-03:00', 'flyer': '2026-03-15_022.jpg', 'place': 'Tandil', 'mode': 'MTB rural', 'status': 'Fecha confirmada, todavía no publicamos la información de esta edición', 'open': False, 'tiers': [], 'cats': {}, 'sched': [], 'dist': {}, 'champ': '', 'incl': '', 'insc': '', 'venue': '', 'org': '', 'info': '', 'series': 'vuelta-escuela-granja'},
]
RACES[0]['series'] = 'rural-bike-mechongue'
RACES[1]['series'] = 'vuelta-coronel-vidal'


def when(r):
    d = datetime.date.fromisoformat(r['date'])
    return f'{DIAS[d.weekday()].capitalize()} {d.day} de {MES[d.month - 1]}' + (f' de {d.year}' if d.year != 2026 else '')


races_json = '<script id="races-data" type="application/json">' + json.dumps([{'id': r['id'], 'name': r['name'], 'start': r['start'], 'when': f"{when(r)} · {r['place']}"} for r in RACES], ensure_ascii=False) + '</script>'


def race_row(r, h='h3'):
    return f"""<li data-race-date="{r['date']}T23:59:00-03:00">
{flyer(r['flyer'], r['name'], 'fl')}
<div class="tx"><{h}><a href="{{{{R}}}}calendario/{r['id']}/">{esc(r['name'])}</a></{h}><p class="when">{when(r)} · {esc(r['place'])}</p><p class="st">{esc(r['status'].split(':')[0].split(', todavía')[0])}</p></div>
</li>"""


# ---------------------------------------------------------------- Portada
FRAME = ['largada-mtb-arco-negro-peloton', 'largada-running-arco-rojo', 'arco-bienvenidos-rojo-ciclistas', 'corredores-reunidos-previa', 'ciclista-barro-arco-negro']
frame = ''.join((f'<img class="on" src="{{{{R}}}}assets/img/{n}.webp" alt="{esc(PH[n]["alt"])}" fetchpriority="high">' if i == 0 else f'<img data-src="{{{{R}}}}assets/img/{n}.webp" alt="{esc(PH[n]["alt"])}">') for i, n in enumerate(FRAME))

STEPS = [
 ('2006', 'ciclista-barro-bosque', 'Cámaras de camión y un arroyo', '29 de enero, Club Independiente de Ayacucho. Campo Aventura: 8 horas, 51 participantes corriendo, pedaleando y navegando el arroyo Tandileofú en balsas hechas con cámaras de camión. En abril, 162 atletas en el Maratón Fiesta del Ternero.'),
 ('2007', 'arco-bienvenidos-rojo-ciclistas', 'De dónde sale el nombre', 'Entrenando kilómetros y kilómetros para el Cruce de los Andes, 104 km en tres etapas. Ahí nos cayó la ficha: no hay límite, solo el que nosotros nos pongamos. Y entró la invitación del Ayacucho Cicles Club para organizar su ciclismo rural.'),
 ('2008', 'largada-mtb-arco-negro-peloton', 'El primer campeonato', 'Cuatro fechas de ciclismo rural en Ayacucho y 362 ciclistas sumando todas. Ese año también largamos un biatlón a las 12.30 en vez de a las 10, porque la niebla no dejaba ver a dos metros.'),
 ('2009', 'podio-running-mar-de-cobo', 'Nos llaman de afuera', 'Primera vez fuera de Ayacucho: el Rally de Barker–Villa Cacique, con 105 ciclistas. A fin de año, 99 en el Rural Bike de la Sociedad Rural: con lo recaudado, A.P.I.D.D.A. compró una fotocopiadora.'),
 ('2010', 'ciclista-barro-arco-negro', 'Rauch, bajo el agua', 'Fiscalización y locución del 1º Rural Bike Ciudad de Rauch: 147 bikers y una lluvia enorme. Terminaron igual. Desde ese año los resultados y las fotos van a la web.'),
 ('2024', 'ciclista-barro-bosque-rosa', 'Sudamericano en Balcarce', 'Clasificaciones del Campeonato Sudamericano de MTB, del 11 al 13 de octubre, y de los 1ros. Juegos Juveniles Nacionales de MTB, el 10.'),
 ('2026', 'corredores-reunidos-previa', '20 años no es nada', f'17° Campeonato KMI, Copa Bikes Amigorena. Y en esta web, {miles(S["results_unique"])} resultados de {miles(S["runners"])} corredores, buscables por nombre. Seguimos con la misma frase: único límite, tu imaginación.'),
]
story = '<section class="story" aria-label="Historia de Kilómetro Infinito"><div class="story-bg" aria-hidden="true">' + ''.join(f'<img {"class=on " if i == 0 else ""}src="{{{{R}}}}assets/img/{p}.webp" alt="" loading="{"eager" if i == 0 else "lazy"}">' for i, (y, p, t, x) in enumerate(STEPS)) + '</div><div class="story-steps">' + ''.join(
    f'<article class="step" data-y="{y}" data-i="{i}"><div class="card-g"><div class="y">{y}</div><h3>{t}</h3><p>{x}</p>{"<p class=note>Las fotos son de carreras de los últimos años.</p>" if i == 0 else ""}</div></article>' for i, (y, p, t, x) in enumerate(STEPS)) + '</div></section>'

top = json.load(open(SITE / 'assets/data/names.json', encoding='utf8'))[:20]
PHOTO_MOS = [('a', 'corredores-reunidos-previa'), ('b', 'operador-crono-notebook'), ('b', 'copas-mesa-premios'), ('b', 'duatleta-corriendo-numero'), ('b', 'ciclista-barro-bosque-rosa'), ('c', 'adrian-poo-selfie-sombrero'), ('e', 'eucaliptos-curva-mtb'),
             ('f', 'corredoras-sonrientes-podio'), ('g', 'saludo-bajo-arco-largada-mar-de-cobo'), ('d', 'arco-negro-llegada-camino'), ('e', 'podio-running-mar-de-cobo'), ('c', 'ciclista-entre-eucaliptos'), ('c', 'bicicleta-roja-detalle'), ('g', 'arco-bienvenidos-rojo-ciclistas'), ('f', 'ciclista-remera-colorida')]


def mosaic(items):
    return '<div class="mosaic">' + ''.join(f'<button class="{c}" data-lb="{{{{R}}}}assets/img/{n}.webp" aria-label="Ampliar: {esc(PH[n]["alt"])}">{img(n)}</button>' for c, n in items) + '</div>'


# mapa propio con coordenadas reales
COAST = [(-35.75, -57.32), (-36.0, -57.45), (-36.25, -57.15), (-36.29, -56.78), (-36.72, -56.68), (-37.11, -56.86), (-37.26, -56.97), (-37.75, -57.42), (-38.0, -57.54), (-38.27, -57.84), (-38.58, -58.7), (-38.86, -60.07), (-38.98, -60.9)]


def mp(la, lo):
    return round((lo + 61.0) / 4.6 * 800, 1), round((la + 35.6) / -3.5 * 620, 1)


LABELS = {'Ayacucho', 'Tandil', 'Balcarce', 'Rauch', 'Mar del Plata', 'Miramar', 'Villa Gesell', 'Costa del Este', 'General Lavalle', 'Coronel Vidal', 'Quequén', 'Mechongué', 'Maipú', 'Olavarría', 'Dolores', 'Pila'}
mapsvg = '<svg viewBox="0 0 800 620" role="img" aria-label="Mapa del sudeste bonaerense con las localidades donde cronometramos"><polyline class="coast" points="' + ' '.join(f'{mp(*c)[0]},{mp(*c)[1]}' for c in COAST) + '"/>'
for n, c, la, lo in ST['places']:
    x, y = mp(la, lo)
    r = 4 + c ** .5 * 1.9
    t = f'<text x="{x + r + 5}" y="{y + 5}">{esc(n)}</text>' if n in LABELS else ''
    if n in ('Villa Gesell', 'Costa del Este', 'General Lavalle', 'Mar del Plata', 'Miramar', 'Quequén') and t:
        t = f'<text x="{x - r - 5}" y="{y + 5}" text-anchor="end">{esc(n)}</text>' if n in ('Mar del Plata', 'Miramar', 'Quequén') else t
    mapsvg += f'<g><title>{esc(n)}: {c} {"carrera" if c == 1 else "carreras"}</title><circle cx="{x}" cy="{y}" r="{r:.1f}"/>{t}</g>'
mapsvg += '</svg>'
place_list = ''.join(f'<li>{esc(n)} <b>{c}</b></li>' for n, c, *_ in ST['places'][:22])

home = f'''
<section class="hero">
<div class="frame" data-swap>{frame}</div>
<div class="hero-in"><div class="wrap hero-g">
<div>
<h1>Kilómetro Infinito</h1>
<p class="lead">Cronometramos carreras de mountain bike, duatlón y running en el sudeste bonaerense desde 2006.</p>
<div class="btns"><a class="btn y" href="{{{{R}}}}calendario/">Calendario e inscripción</a><a class="btn line" href="{{{{R}}}}resultados/">Ver resultados</a></div>
</div>
<div class="nextcard" data-nextbar>
<p class="lbl">Próxima carrera</p>
<a class="t" data-n-name href="{{{{R}}}}calendario/{RACES[0]['id']}/">{esc(RACES[0]['name'])}<span class="d" data-n-when>{when(RACES[0])} · {RACES[0]['place']}</span></a>
<div class="clock" data-clock="{RACES[0]['start']}" aria-label="Tiempo hasta la largada">0d 00:00:00</div>
<a class="btn w" style="width:100%;min-height:44px;padding:8px 18px" data-n-btn href="{{{{R}}}}calendario/{RACES[0]['id']}/">Ver carrera</a>
</div>
</div></div>
</section>
{races_json}

<section class="full find on-ink">{img('arco-negro-llegada-camino', 'bg') if False else img('largada-running-arco-rojo', 'bg')}<div class="wrap">
<div class="bigfig" data-count="{S['results_unique']}">{miles(S['results_unique'])}</div>
<h2>tiempos publicados. Alguno es tuyo.</h2>
{finder()}
<p class="try">Probá con <a href="{{{{R}}}}corredor/?n={esc(top[0][0])}">{esc(top[0][0])}</a>, que corrió {top[0][1]} carreras, o con <a href="{{{{R}}}}corredor/?n={esc(top[1][0])}">{esc(top[1][0])}</a>, que corrió {top[1][1]}.</p>
<div class="figs"><div><b>{S['events']}</b>carreras en la web</div><div><b>{miles(S['runners'])}</b>corredores distintos</div><div><b>{S['places']}</b>localidades</div><div><b>20</b>años de crono</div></div>
</div></section>

<section class="sec yel"><div class="wrap">
<div class="sec-h"><h2>Lo que viene</h2><p>En cada carrera ponés tu año de nacimiento y te decimos tu categoría y cuánto pagás hoy.</p></div>
<ul class="lineup">{''.join(race_row(r) for r in RACES)}</ul>
</div></section>

{story}

<section class="sec"><div class="wrap scene">
<div class="pic rv">{img('adrian-poo-sombrero-carpa')}</div>
<div>
<h2>Vos organizás. El reloj es nuestro.</h2>
<ul class="say">
<li class="rv"><h3>Antes de largar</h3><p>Podemos tomar las preinscripciones, confirmar los pagos por mail y dejar la lista de inscriptos a la vista de todos, como en Coronel Vidal y Mechongué.</p></li>
<li class="rv"><h3>En la largada y la llegada</h3><p>Cronometramos con tiempos por vuelta, y locución si la querés: fue lo que hicimos en Rauch en 2010 y lo seguimos haciendo con el sombrero puesto.</p></li>
<li class="rv"><h3>Esa misma tarde</h3><p>Clasificación por categoría y general publicada en la web, con diferencias y promedio. Y si tu carrera suma a un campeonato, también los puntos.</p></li>
</ul>
<a class="btn" href="{{{{R}}}}cronometraje/">Pedir presupuesto</a>
</div>
</div></section>

<section class="full quote on-ink">{img('ciclista-barro-bosque-rosa', 'bg')}<div class="wrap"><p>Único límite, tu imaginación.</p></div></section>

<section class="sec"><div class="wrap">
<div class="sec-h"><h2>Barro, arcos y podios</h2><p>Sacadas en las carreras y publicadas en nuestro Instagram, <a href="{IG}" rel="noopener">@kminfinito</a>.</p></div>
{mosaic(PHOTO_MOS)}
<p style="margin-top:22px"><a class="btn line" href="{{{{R}}}}fotos/">Ver todas las fotos y los afiches</a></p>
</div></section>

<section class="sec ink on-ink"><div class="wrap mapg">
<div class="rv">{mapsvg}</div>
<div><h2>De Rauch a Quequén</h2><p style="margin:16px 0 22px;max-width:44ch">Carreras con resultados en esta web, por localidad. Balcarce va primero, pero Ayacucho es la casa.</p><ul class="places">{place_list}</ul></div>
</div></section>

<section class="sec soft"><div class="wrap faqg">
{img('corredoras-sonrientes-podio')}
<div><h2 style="margin-bottom:22px">Lo que más nos preguntan</h2>
{''.join(f'<details{" open" if i == 0 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for i, (q, a) in enumerate(FAQ))}
</div></div></section>

<section class="full contact on-ink">{img('arco-bienvenidos-rojo-ciclistas', 'bg')}<div class="wrap">
<h2 style="margin-bottom:14px">Escribinos</h2>
<a class="mail" href="mailto:{MAIL}">{MAIL}</a>
<div class="btns" style="margin-top:22px"><a class="btn y" href="https://wa.me/{WA}?text={esc('Hola Adrián! Te escribo desde la web de KMI.')}" rel="noopener">WhatsApp (0249) 15-455-1251</a><a class="btn line" href="{IG}" rel="noopener">Instagram @kminfinito</a></div>
</div></section>
'''
page('index.html', 'Kilómetro Infinito | Cronometraje de carreras de MTB, duatlón y running', f'Cronometraje y clasificaciones de carreras en el sudeste bonaerense desde 2006. Buscá tu nombre entre {miles(S["results_unique"])} resultados y mirá el calendario con inscripción.', home, schema=[ORG, faq_schema(FAQ)])

# ---------------------------------------------------------------- Calendario
cal = f'''<section class="ph"><div class="wrap"><h1>Calendario</h1><p class="lead">Las carreras con el crono de KMI que vienen en lo que queda de 2026 y lo que ya hay confirmado de 2027.</p></div></section>
{races_json}
<section class="sec"><div class="wrap"><ul class="lineup">{''.join(race_row(r, 'h2') for r in RACES)}</ul>
<p style="margin-top:34px;max-width:60ch"><b>Suspendida:</b> el Duatlón Rural de Coronel Vidal del 1° de noviembre, final del Campeonato Tres Pueblos.</p></div></section>
<section class="sec soft"><div class="wrap two"><div><h2>¿Cómo me anoto?</h2><p style="margin-top:14px;max-width:44ch">Formulario, mail, pago, comprobante. Te lo contamos paso a paso.</p><p style="margin-top:20px"><a class="btn" href="{{{{R}}}}inscripcion/">Cómo inscribirme</a></p></div>{img('corredores-reunidos-previa')}</div></section>'''
page('calendario/index.html', 'Calendario de carreras 2026 y 2027 | Kilómetro Infinito', 'Próximas carreras cronometradas por KMI: Rural Bike Mechongué, Vuelta a Coronel Vidal, Caminos de Luna, Vuelta a Batán y Escuela Granja. Categorías, precios e inscripción.', cal, 'calendario/', band='saludo-bajo-arco-largada-mar-de-cobo')

MOD = {'comp': 'Competitiva', 'promo': 'Promocional', 'prin': 'Principiante'}
MODS = {'comp': 'Competitivas', 'promo': 'Promocionales', 'prin': 'Principiantes'}
for r in RACES:
    tiers = ''
    if r['tiers']:
        cols = [m for m in ('comp', 'promo', 'prin') if m in r['tiers'][0]]
        tiers = '<div class="tiers">' + ''.join(
            f'<div class="tier" data-from="{t["from"]}" data-to="{t["to"]}"><span class="small">Del {fdate(t["from"], False)} al {fdate(t["to"], False)}</span>' + ''.join(f'<b class="num">$ {miles(t[m])}</b><span class="small">{MODS[m]}</span>' for m in cols) + '</div>' for t in r['tiers']) + '</div>'
    cats_html = ''
    if r['cats']:
        for m, gs in r['cats'].items():
            cats_html += f'<h3 style="margin-top:22px">{MODS[m]}' + (f' · {r["dist"].get(m)}' if r['dist'].get(m) else '') + '</h3><p style="margin-top:6px;max-width:80ch">' + ' · '.join(c[0] + (f' ({c[1]} a {c[2]})' if c[1] and c[2] < 200 else (f' (hasta {c[2]})' if not c[1] else f' ({c[1]} y más)')) for g in ('d', 'c') for c in gs[g]) + '</p>'
    facts = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in [
        ('Cuándo', when(r)), ('Dónde', esc(r.get('venue') or r['place']) + (f' · <a href="{r["map"]}" rel="noopener">Ver en el mapa</a>' if r.get('map') else '')), ('Modalidad', esc(r['mode'])), ('Organiza', esc(r.get('org', ''))), ('Campeonato', esc(r.get('champ', ''))), ('Informes', (f'<a href="tel:{r["infoTel"]}">{r["info"]}</a> · ' if r.get('info') else '') + f'<a href="mailto:{MAIL}">{MAIL}</a>')] if v)
    sched = ''.join(f'<dt>{a}</dt><dd>{esc(b)}</dd>' for a, b in r['sched'])
    tool = ''
    if r['open']:
        opts = ''.join(f'<option value="{m}">{MOD[m]} · {r["dist"].get(m, "")}</option>' for m in r['cats'])
        data = {k: r[k] for k in ('tiers', 'cats', 'dist')}
        data['year'] = 2026
        tool = f'''<section class="sec" id="inscripcion"><div class="wrap two">
<div class="tool on-ink" id="catfinder"><h2>Tu categoría y cuánto pagás hoy</h2>
<div class="tool-g"><div><label for="cf-year">Año de nacimiento</label><input id="cf-year" type="number" inputmode="numeric" placeholder="1985" min="1920" max="2020"></div>
<div><label for="cf-g">Rama</label><select id="cf-g"><option value="c">Caballeros</option><option value="d">Damas</option></select></div>
<div><label for="cf-mod">Modalidad</label><select id="cf-mod">{opts}</select></div></div>
<div class="out" id="cf-out" hidden aria-live="polite"></div>
<div class="btns" style="margin-top:20px"><a class="btn y" href="{FORM}" rel="noopener">Preinscribirme</a>{f'<a class="btn line" href="{r["insc"]}" rel="noopener">Ver inscriptos</a>' if r['insc'] else ''}</div>
<p class="small" style="margin-top:14px">Te respondemos por mail de lunes a viernes, a las 13 y a las 20. Revisá spam.</p>
</div>
<div><h2>Precios por fecha</h2>{tiers}<p style="margin-top:18px">{esc(r.get('refund', ''))}</p><p style="margin-top:10px"><b>Incluye:</b> {esc(r['incl'])}</p>{f'<p style="margin-top:10px"><b>Premios:</b> {esc(r["prizes"])}</p>' if r.get('prizes') else ''}
<p style="margin-top:10px"><b>En persona:</b> Bikes Amigorena, Colón 7199, Mar del Plata, o con nosotros en las carreras previas.</p></div>
</div></section>
<section class="sec soft"><div class="wrap"><h2>Todas las categorías</h2><p style="margin-top:8px">Edad al 31 de diciembre de 2026.</p>{cats_html}</div></section>
<script id="race-data" type="application/json">{json.dumps(data, ensure_ascii=False)}</script>'''
    elif r.get('incl'):
        tool = f'''<section class="sec"><div class="wrap two"><div><h2>Distancias</h2><div class="tiers">{''.join(f'<div class="tier"><b class="num">{v}</b><span class="small">{MOD[k]}</span></div>' for k, v in r['dist'].items())}</div><p style="margin-top:18px"><b>Incluye:</b> {esc(r['incl'])}</p>
<div class="btns" style="margin-top:20px">{f'<a class="btn" href="{r["insc"]}" rel="noopener">Ver inscriptos</a>' if r['insc'] else ''}</div></div>{flyer(r['flyer'], r['name'])}</div></section>'''
    past = ''
    sid = r.get('series')
    if sid and sid in SER:
        eds = [E[i] for i in SER[sid]['editions']][:6]
        past = f'''<section class="sec yel"><div class="wrap"><div class="sec-h"><h2>Ediciones anteriores</h2><p><a href="{{{{R}}}}competencias/{sid}/">Toda la historia de {esc(SER[sid]['name'])}</a></p></div><ul class="races">{''.join(race_li(e) for e in eds) if False else ''}</ul>{'<div class="cards">' + ''.join(f'<a href="{{{{R}}}}p/{e["pages"][0]["slug"]}.html">{flyer(e["flyer"], e["name"])}<h3>{esc(e["name"])}</h3><p class="small">{fdate(e["date"])} · {e["n"]} corredores</p></a>' for e in eds if e['flyer']) + '</div>'}</div></section>'''
    body = f'''<section class="ph"><div class="wrap ph-g"><div><p class="crumbs"><a href="{{{{R}}}}calendario/">Calendario</a></p><h1 class="mid">{esc(r['name'])}</h1><p class="lead">{when(r)} · {esc(r['place'])}</p><p style="margin-top:8px;font-weight:600">{esc(r['status'])}</p></div>{flyer(r['flyer'], r['name'], '', False)}</div></section>
<section class="nextbar on-ink"><div class="wrap" style="grid-template-columns:minmax(0,1fr) auto"><div class="clock" data-clock="{r['start']}" data-done="Ya se corrió">0d 00:00:00</div>{'<a class="btn y" href="#inscripcion">Inscribirme</a>' if r['open'] else ''}</div></section>
<section class="sec"><div class="wrap two"><dl class="facts">{facts}</dl><dl class="facts">{sched}</dl></div></section>
{tool}{past}'''
    schema = [{'@context': 'https://schema.org', '@type': 'SportsEvent', 'name': r['name'], 'startDate': r['start'], 'eventStatus': 'https://schema.org/EventScheduled', 'location': {'@type': 'Place', 'name': r.get('venue') or r['place'], 'address': {'@type': 'PostalAddress', 'addressLocality': r['place'], 'addressRegion': 'Buenos Aires', 'addressCountry': 'AR'}}, 'organizer': {'@type': 'Organization', 'name': r.get('org') or 'Kilómetro Infinito'}}]
    page(f'calendario/{r["id"]}/index.html', f'{r["name"]}, {fdate(r["date"])} | Inscripción y categorías', f'{r["name"]} en {r["place"]}, {fdate(r["date"])}. {r["status"]}. Categorías, precios por fecha e inscripción.', body, 'calendario/', schema=schema)
    if r.get('old'):
        page(f'p/{r["old"]}.html', r['name'], r['status'], f'<section class="ph"><div class="wrap"><h1 class="mid">{esc(r["name"])}</h1><p class="lead"><a href="{{{{R}}}}calendario/{r["id"]}/">Esta carrera se mudó acá</a></p></div></section><script>location.replace("../calendario/{r["id"]}/")</script>', noindex=True, sitemap=False)

# ---------------------------------------------------------------- Resultados
def race_li(e):
    gen = next((p for p in e['pages'] if p['kind'] == 'general'), None)
    cat = next((p for p in e['pages'] if p['kind'] == 'categorias'), None)
    first = (cat or gen or e['pages'][0])['slug']
    th = flyer(e['flyer'], e['name']) or '<div class="noimg" aria-hidden="true">KMI</div>'
    meta = ' · '.join(x for x in [fdate(e['date']), e['place'], f"{e['n']} en la clasificación"] if x)
    win = f"<br><span class='small'>Primero en la general: {esc(e['winner']['name'])}, {esc(e['winner']['time'])}</span>" if e.get('winner') else ''
    btn = ''.join(f'<a class="btn line" href="{{{{R}}}}p/{p["slug"]}.html">{"Categorías" if p["kind"] == "categorias" else "General" if p["kind"] == "general" else "Ver"}</a>' for p in e['pages'][:3])
    return f'<li data-y="{e["date"][:4]}" data-d="{esc(e["disc"])}" data-p="{esc(e["place"])}" data-k="{esc(e["name"] + " " + e["place"])}">{th}<div><h3><a href="{{{{R}}}}p/{first}.html">{esc(e["name"])}</a></h3><p class="small">{esc(meta)}{win}</p></div><div class="btns">{btn}</div></li>'


by_year = collections.defaultdict(list)
for e in E:
    by_year[e['date'][:4]].append(e)
years = sorted(by_year, reverse=True)
listing = ''.join(f'<div class="year" data-year="{y}">{y}</div><ul class="races">{"".join(race_li(e) for e in by_year[y])}</ul>' for y in years)
rank = ''.join(f'<li><a href="{{{{R}}}}corredor/?n={esc(n)}">{esc(n)}<span>{c} carreras</span></a></li>' for n, c in top)
places_opts = ''.join(f'<option>{esc(n)}</option>' for n in sorted({e['place'] for e in E if e['place']}))
disc_opts = ''.join(f'<option>{esc(n)}</option>' for n, _ in collections.Counter(e['disc'] for e in E).most_common())
res = f'''<section class="ph"><div class="wrap"><h1>Resultados</h1><p class="lead">{S['events']} carreras con clasificación, desde {years[-1]}. Escribí tu nombre y te mostramos todas las tuyas.</p>{finder('res')}</div></section>
<section class="sec" style="padding-top:clamp(30px,4vw,60px)"><div class="wrap" id="race-list">
<div class="tools"><input id="rl-q" type="search" placeholder="Buscar carrera o lugar" aria-label="Buscar carrera o lugar">
<select id="rl-y" aria-label="Año"><option value="">Todos los años</option>{''.join(f'<option>{y}</option>' for y in years)}</select>
<select id="rl-d" aria-label="Disciplina"><option value="">Todas las disciplinas</option>{disc_opts}</select>
<select id="rl-p" aria-label="Lugar"><option value="">Todos los lugares</option>{places_opts}</select><span id="rl-c" class="small" aria-live="polite">{S['events']} carreras</span></div>
{listing}
<p style="margin-top:40px"><a class="btn line" href="{{{{R}}}}archivo/">Ver el archivo 2010 a 2014</a></p>
</div></section>
<section class="sec ink on-ink"><div class="wrap two"><div><h2>Los que más corrieron</h2><p style="margin-top:14px;max-width:40ch">Contando las clasificaciones publicadas en esta web. Si dos personas se llaman igual, acá cuentan como una; y si te anotaste de dos formas distintas, como dos.</p></div><ol class="rank">{rank}</ol></div></section>'''
page('resultados/index.html', 'Resultados y clasificaciones de carreras | Kilómetro Infinito', f'Clasificaciones de {S["events"]} carreras de MTB, duatlón y running del sudeste bonaerense. Buscá tu nombre y encontrá tus tiempos.', res, 'resultados/', band='ciclista-barro-arco-negro')

# Ficha de corredor
prof = f'''<section class="ph" id="perfil"><div class="wrap"><p class="crumbs"><a href="{{{{R}}}}resultados/">Resultados</a></p><h1 class="mid" id="p-name">Buscá tu nombre</h1>
<p id="p-none" hidden class="lead">No encontramos ese nombre tal cual. Probá de nuevo, solo con el apellido.</p>{finder('p')}</div></section>
<section class="sec" id="p-data" hidden><div class="wrap">
<div class="figs" id="p-figs" style="margin-top:0"></div>
<div class="two" style="margin-top:clamp(30px,5vw,60px)"><div><h2 style="font-size:var(--lead)">Carreras por año</h2><div class="bars" id="p-bars"></div><div class="barl" id="p-bl"></div></div><div><h2 style="font-size:var(--lead);margin-bottom:12px">Dónde corriste</h2><ul class="places" id="p-places"></ul></div></div>
<div class="btns" style="margin-top:26px"><button class="btn" id="p-share">Compartir mis resultados</button><a class="btn line" href="{{{{R}}}}calendario/">Anotarme en la próxima</a></div>
<h2 style="margin-top:clamp(40px,6vw,80px);margin-bottom:16px">Todas tus carreras</h2>
<div class="tbl-w"><table><thead><tr><th>Pos.</th><th>Carrera</th><th>Fecha</th><th class="hm">Lugar</th><th class="hm">Categoría</th><th>Tiempo</th></tr></thead><tbody id="p-rows"></tbody></table></div>
<p class="small" style="margin-top:14px">La posición es la de tu categoría cuando la clasificación se publicó por categorías. Si dos personas se llaman igual, acá aparecen juntas. Si ves un error, <a href="mailto:{MAIL}">escribinos</a>.</p>
</div></section>'''
page('corredor/index.html', 'Tus resultados | Kilómetro Infinito', 'Todas tus carreras con el crono de KMI: posición, tiempo, podios y localidades.', prof, 'resultados/', noindex=True, sitemap=False)

# Tablas (mismas URLs viejas)
COLS = [('posg', 'Gral.', 'hm'), ('pos', 'Pos.', ''), ('cat', 'Cat.', 'hm'), ('name', 'Corredor', 'n'), ('bib', 'Placa', 'hm'), ('from', 'Procedencia', 'hm'), ('time', 'Tiempo', ''), ('gap', 'Dif.', 'hm'), ('avg', 'Prom.', 'hm')]
count_p = 0
for f in glob.glob(str(D / 'results' / '*.json')):
    d = json.load(open(f, encoding='utf8'))
    slug = d['slug']
    e = ev_by_slug.get(slug)
    secs = d['sections']
    blocks, opts = '', ''
    for i, s in enumerate(secs):
        pair = sum(' / ' in r.get('name', '') for r in s['rows']) > len(s['rows']) / 2
        nm = s['name'] or (('Parejas' if pair else 'Individuales') if len(secs) > 1 else 'Clasificación general')
        sid = f's{i}'
        opts += f'<option value="{sid}">{esc(nm)}</option>'
        have = [c for c in COLS if any(r.get(c[0]) for r in s['rows'])]
        nspl = max((len(r.get('splits', [])) for r in s['rows']), default=0)
        th = ''
        for c in have:
            if c[0] == 'time':
                th += ''.join(f'<th class="hm">Vta. {k + 1}</th>' for k in range(nspl))
            th += f'<th class="{c[2] if c[2] == "hm" else ""}">{c[1]}</th>'
        rows = ''
        for r in s['rows']:
            pn = re.match(r'^(\d+)', r.get('pos', '') or '')
            pod = ' class="pod"' if pn and int(pn.group(1)) <= 3 else ''
            tds = ''
            for c in have:
                v = esc(r.get(c[0], ''))
                if c[0] == 'time':
                    sp = r.get('splits', [])
                    tds += ''.join(f'<td class="hm">{esc(sp[k]) if k < len(sp) else ""}</td>' for k in range(nspl))
                if c[0] == 'name':
                    links = ' / '.join(f'<a href="../corredor/?n={esc(x.strip())}">{esc(x.strip())}</a>' for x in r.get('name', '').split('/'))
                    tds += f'<td class="n">{links}</td>'
                else:
                    tds += f'<td class="{c[2] if c[2] == "hm" else ""}">{v}</td>'
            rows += f'<tr{pod}>{tds}</tr>'
        blocks += f'<section class="sect" id="{sid}"><h2>{esc(nm)}</h2><div class="tbl-w"><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div></section>'
    name = e['name'] if e else d['title']
    date = e['date'] if e else d['date']
    place = e['place'] if e else ''
    sib = ''
    if e and len(e['pages']) > 1:
        sib = '<div class="chips">' + ''.join(f'<a class="chip {"on" if p["slug"] == slug else ""}" href="{p["slug"]}.html">{"Por categorías" if p["kind"] == "categorias" else "General" if p["kind"] == "general" else esc(p["title"])[:30]}</a>' for p in e['pages']) + '</div>'
    ser = f'<a href="{{{{R}}}}competencias/{e["series"]}/">{esc(SER[e["series"]]["name"])}</a> · ' if e and e.get('series') and e['series'] in SER else ''
    fl = flyer(e['flyer'], name) if e else ''
    kind = 'general' if 'general' in d['title'].lower() else 'por categorías' if 'categ' in d['title'].lower() else ''
    tot = sum(len(s['rows']) for s in secs)
    bodyp = f'''<section class="ph"><div class="wrap{' ph-g' if fl else ''}"><div><p class="crumbs"><a href="{{{{R}}}}resultados/">Resultados</a></p><h1 class="mid">{esc(name)}</h1><p class="lead">{ser}{fdate(date)}{' · ' + esc(place) if place else ''} · {tot} en la clasificación{' ' + kind if kind else ''}</p>{sib}</div>{fl}</div></section>
<section class="sec" id="res" style="padding-top:12px"><div class="wrap"><div class="tools"><input id="res-q" type="search" placeholder="Buscá tu nombre, placa o ciudad" aria-label="Filtrar la tabla">{f'<select id="res-cat" aria-label="Ir a la categoría"><option value="">Ir a la categoría</option>{opts}</select>' if len(secs) > 1 else ''}</div>{blocks}
<p class="small" style="margin-top:26px"><a href="{{{{R}}}}calendario/">Próximas carreras</a> · ¿Ves un error? <a href="mailto:{MAIL}">Escribinos</a></p></div></section>'''
    page(f'p/{slug}.html', f'{name} {date[:4]} | Clasificación{" " + kind if kind else ""}', f'Clasificación{" " + kind if kind else ""} de {name}, {fdate(date)}{", " + place if place else ""}: {tot} corredores, tiempos y posiciones. Cronometró KMI.', bodyp, 'resultados/')
    count_p += 1

# ---------------------------------------------------------------- Competencias
BANDS = ['ciclista-barro-arco-negro', 'largada-mtb-arco-negro-peloton', 'arco-bienvenidos-rojo-ciclistas', 'ciclista-barro-bosque', 'ciclista-barro-bosque-rosa', 'corredores-reunidos-previa']
cards = ''
for sid, s in sorted(SER.items(), key=lambda kv: -len(kv[1]['editions'])):
    eds = [E[i] for i in s['editions']]
    fl = next((e['flyer'] for e in eds if e['flyer']), None)
    cards += f'<a href="{sid}/" class="rv"><div>{flyer(fl, s["name"])}<h3>{esc(s["name"])}</h3><p class="small">{esc(s["place"])} · {len(eds)} ediciones con clasificación</p></div></a>'
    bars = ''
    chrono = sorted(eds, key=lambda e: e['date'])
    mx = max(e['n'] for e in eds) or 1
    bars = ''.join(f'<i title="{e["date"][:4]}: {e["n"]}" style="height:{max(3, e["n"] / mx * 100):.0f}%"></i>' for e in chrono)
    rowsS = ''.join(f'<tr><td class="n"><a href="../../p/{e["pages"][0]["slug"]}.html">{esc(e["name"])}</a></td><td style="white-space:nowrap">{fdate(e["date"])}</td><td>{e["n"]}</td><td class="hm">{esc(e.get("winner", {}).get("name", ""))}</td><td class="hm">{esc(e.get("winner", {}).get("time", ""))}</td></tr>' for e in eds)
    gallery = ''.join(f'<figure style="margin:0"><button data-lb="{{{{R}}}}assets/afiches/{e["flyer"][:-4]}.webp" aria-label="Ampliar afiche">{flyer(e["flyer"], e["name"])}</button><figcaption>{e["date"][:4]}</figcaption></figure>' for e in eds if e['flyer'] and (SITE / 'assets/afiches' / (e['flyer'][:-4] + '.webp')).exists())
    up = next((r for r in RACES if r.get('series') == sid), None)
    b = f'''<section class="ph"><div class="wrap"><p class="crumbs"><a href="{{{{R}}}}competencias/">Competencias</a></p><h1 class="mid">{esc(s['name'])}</h1><p class="lead">{esc(s['place'])}. {len(eds)} ediciones con clasificación en esta web y {miles(s['total'])} corredores clasificados en total.</p>{f'<p style="margin-top:18px"><a class="btn" href="{{{{R}}}}calendario/{up["id"]}/">Próxima: {esc(up["name"])}</a></p>' if up else ''}</div></section>
<section class="sec ink on-ink"><div class="wrap two"><div><h2>Corredores por edición</h2><div class="bars">{bars}</div><div class="barl"><span>{chrono[0]['date'][:4]}</span><span>{chrono[-1]['date'][:4]}</span></div></div><div><h2>Buscate</h2>{finder('s', label='Tu nombre o apellido')}</div></div></section>
<section class="sec"><div class="wrap"><h2 style="margin-bottom:18px">Todas las ediciones</h2><div class="tbl-w"><table><thead><tr><th>Edición</th><th>Fecha</th><th>Clasificados</th><th class="hm">Primero en la general</th><th class="hm">Tiempo</th></tr></thead><tbody>{rowsS}</tbody></table></div></div></section>
{f'<section class="sec soft"><div class="wrap"><h2 style="margin-bottom:18px">Los afiches, año por año</h2><div class="pgrid af">{gallery}</div></div></section>' if gallery else ''}'''
    page(f'competencias/{sid}/index.html', f'{s["name"]}: resultados e historia | KMI', f'{s["name"]} en {s["place"]}: {len(eds)} ediciones, ganadores, cantidad de corredores por año y clasificaciones completas.', b, 'competencias/', band=BANDS[sum(map(ord, sid)) % len(BANDS)])
page('competencias/index.html', 'Competencias clásicas de MTB y duatlón | Kilómetro Infinito', 'Las carreras que se repiten año a año con el crono de KMI: Vuelta a Gardey, Desafío de las Tres Cruces, Desafío de los Leones, Rally Costa del Este y más.',
     f'<section class="ph"><div class="wrap"><h1>Competencias</h1><p class="lead">Las que vuelven todos los años. Entrás a cualquiera y ves sus ediciones, quién ganó y los afiches.</p></div></section><section class="sec"><div class="wrap cards">{cards}</div></section>', 'competencias/', band='largada-mtb-arco-negro-peloton')

# ---------------------------------------------------------------- Campeonatos
FECHAS = [('2026-04-19', 'Ayacucho', 'KMI MTB Timing, 20 años de KMI'), ('2026-05-03', 'Rauch', 'Hangar Race Bike'), ('2026-06-07', 'Miramar', 'Rally Cross Miramar'), ('2026-07-12', 'Balcarce', 'Las 3 hs de MTB'), ('2026-08-02', 'Mar de las Pampas', 'Rally Bike Mar de las Pampas'), ('2026-08-09', 'Ayacucho', 'Temple de Acero “El Desafío”'), ('2026-08-23', 'Azucena', '2ª Vuelta a Azucena'), ('2026-09-13', 'Mar del Plata', 'Rally Mar y Sierras'), ('2026-11-08', 'Mechongué', 'Rural Bike ACEPT'), ('2026-11-22', 'Coronel Vidal', 'Rally Bike Vidal Bike, la final')]
pts = [50, 45, 40, 35, 30, 25, 20, 15, 10, 5]
champs = [e for e in E if e['disc'] == 'Campeonato']
camp = f'''<section class="ph"><div class="wrap"><h1>Campeonatos</h1><p class="lead">Diecisiete ediciones sumando puntos. Esta se llama “20 años no es nada” y es la Copa Bikes Amigorena.</p><div class="btns" style="margin-top:20px"><a class="btn" href="{POS_KMI}" rel="noopener">Ver posiciones actuales</a><a class="btn line" href="{{{{R}}}}p/17-campeonato-kmi-de-mtb-rural-20-anos.html">Reglamento completo</a></div></div></section>
<section class="sec"><div class="wrap two"><div><h2 style="margin-bottom:20px">Las diez fechas</h2><div class="tbl-w"><table><thead><tr><th>Fecha</th><th>Sede</th><th>Carrera</th></tr></thead><tbody>{''.join(f'<tr><td style="white-space:nowrap">{fdate(d, False)}</td><td class="n">{p}</td><td>{esc(n)}</td></tr>' for d, p, n in FECHAS)}</tbody></table></div></div>
<div><h2 style="margin-bottom:16px">Cómo se suma</h2><div class="prose"><p>En cada fecha el puntaje depende de cuántos corren en tu categoría. Si son 10, el primero suma 20, el segundo 18, el tercero 16, y así hasta 2 el décimo. Más 3 puntos por presentismo en cada fecha.</p><p>La final en Coronel Vidal tiene puntaje fijo: {' · '.join(f'{i + 1}º {p}' for i, p in enumerate(pts[:5]))}, y sigue bajando de a 5 hasta el 10º.</p><p>Para pelear el podio hay que correr la final y al menos 3 fechas previas. Si hay empate, define la posición de la final.</p></div>{img('copas-mesa-premios')}</div></div></section>
<section class="sec yel"><div class="wrap two"><div><h2>Campeonato Tres Pueblos</h2><p style="margin-top:14px;max-width:46ch">Duatlón rural por Vivoratá, Coronel Vidal y Mar Chiquita, organizado por DC Eventos Deportivos con el auspicio de la Municipalidad de Mar Chiquita. Nosotros ponemos el crono.</p><div class="btns" style="margin-top:20px"><a class="btn" href="{POS_3P}" rel="noopener">Ver posiciones</a><a class="btn line" href="{{{{R}}}}p/reglamento-del-campeonato-de-duatlon.html">Reglamento</a></div></div>{img('duatleta-corriendo-numero')}</div></section>
<section class="sec"><div class="wrap"><h2 style="margin-bottom:18px">Campeonatos anteriores</h2><ul class="races">{''.join(race_li(e) for e in champs)}</ul></div></section>'''
page('campeonatos/index.html', '17° Campeonato KMI de MTB Rural | Fechas, puntos y posiciones', '17° Campeonato KMI Copa Bikes Amigorena: las diez fechas de 2026, cómo se suman los puntos y las posiciones. También el Campeonato de Duatlón Tres Pueblos.', camp, 'campeonatos/', band='arco-bienvenidos-rojo-ciclistas')

# ---------------------------------------------------------------- Cronometraje (para organizadores)
SERV = [('Cronometraje', 'Tiempo de cada corredor, por vuelta si el circuito las tiene. Rally, rural bike, contrarreloj, duatlón individual y en postas, running.'),
        ('Clasificación', 'Por categoría y general, con diferencia al primero y al de adelante, promedio y procedencia. Publicada en la web, con la URL de tu carrera para compartir.'),
        ('Locución', 'Adrián con el micrófono y el sombrero, en la largada, la llegada y la entrega de premios.'),
        ('Inscripciones', 'Formulario, confirmación por mail, control de pagos y planilla de inscriptos a la vista. Centro de inscripción en Bikes Amigorena, Mar del Plata.'),
        ('Campeonato', 'Si querés, tu fecha puede sumar al Campeonato KMI, con su público fijo que viene a buscar puntos.')]
crono = f'''<section class="ph"><div class="wrap"><h1>Cronometraje</h1><p class="lead">Para clubes, escuelas, municipios y grupos que quieren hacer su carrera bien. Llevamos 20 años y {S['events']} clasificaciones publicadas.</p><p style="margin-top:20px"><a class="btn" href="#presupuesto">Pedir presupuesto</a></p></div></section>
<section class="sec"><div class="wrap scene"><div class="pic rv">{img('adrian-poo-sombrero-locucion')}</div><div><ul class="say" style="margin-top:-24px">{''.join(f'<li class="rv"><h3>{a}</h3><p>{b}</p></li>' for a, b in SERV)}</ul></div></div></section>
<section class="sec ink on-ink"><div class="wrap two"><div><h2>Trabajamos con</h2><p style="margin-top:14px;max-width:44ch">Cicles Club Ayacucho, escuelas como el ACEPT N° 20 de Mechongué, Rotary Club de Villa Gesell Playa, Club de Leones de Balcarce, DC Eventos Deportivos, entre otros. Muchas carreras son a beneficio y lo seguimos cuidando como el primer día.</p></div><div>{mapsvg}</div></div></section>
<section class="sec yel" id="presupuesto"><div class="wrap two"><div><h2>Contanos tu carrera</h2><p style="margin-top:14px;max-width:40ch">Completá lo que sepas. Se arma el mensaje y nos llega por WhatsApp.</p><div style="margin-top:22px">{img('predio-desde-arriba-arco-rojo')}</div></div>
<form class="tool on-ink" id="budget" onsubmit="return false">
<label for="b-name">Nombre de la carrera</label><input id="b-name" placeholder="1° Rural Bike de tu pueblo">
<div class="tool-g"><div><label for="b-disc">Disciplina</label><select id="b-disc"><option>MTB o rural bike</option><option>Duatlón</option><option>Running</option><option>Aventura</option><option>Otra</option></select></div><div><label for="b-date">Fecha</label><input id="b-date" placeholder="Domingo 14 de marzo"></div></div>
<div class="tool-g"><div><label for="b-place">Lugar</label><input id="b-place" placeholder="Localidad"></div><div><label for="b-n">Corredores estimados</label><input id="b-n" inputmode="numeric" placeholder="150"></div></div>
<p style="margin-top:22px"><a class="btn y" id="b-send" data-wa="{WA}" href="https://wa.me/{WA}" rel="noopener">Enviar por WhatsApp</a></p>
</form></div></section>'''
page('cronometraje/index.html', 'Cronometraje de carreras en Buenos Aires | Pedí presupuesto a KMI', 'Cronometraje, clasificación, locución e inscripciones para carreras de MTB, duatlón y running en la provincia de Buenos Aires. 20 años de experiencia. Pedí presupuesto.', crono, 'cronometraje/')

# ---------------------------------------------------------------- Historia
hist = f'''<section class="ph"><div class="wrap"><h1>Historia</h1><p class="lead">Veinte años, contados con los números que fuimos anotando.</p></div></section>
{story}
<section class="sec ink on-ink"><div class="wrap two"><div><h2>Único límite, tu imaginación</h2><p style="margin-top:16px;max-width:46ch">La frase es de 2007 y sigue en el logo, con el sombrero. Antes de cronometrar a otros, corrimos nosotros: calle y aventura por toda la provincia. Por eso sabemos lo que quiere saber un corredor apenas se baja de la bici.</p></div>{img('adrian-poo-selfie-sombrero')}</div></section>
<section class="sec" style="padding-block:30px"><div class="wrap"><p class="small">Las fotos de esta página son de carreras de los últimos años. Las de 2006 a 2010 las estamos buscando en el archivo.</p></div></section>'''
page('historia/index.html', 'Historia de Kilómetro Infinito: 20 años de crono en Ayacucho', 'Cómo nació KMI en Ayacucho en 2006: balsas con cámaras de camión, el Cruce de los Andes que le dio nombre, el primer campeonato y 20 años de carreras.', hist, 'historia/')

# ---------------------------------------------------------------- Fotos
allp = sorted(n for n in PH)
grid = ''.join(f'<figure style="margin:0"><button data-lb="{{{{R}}}}assets/img/{n}.webp" aria-label="Ampliar: {esc(PH[n]["alt"])}">{img(n)}</button></figure>' for n in allp)
aff = [p for p in sorted((SITE / 'assets/afiches').glob('*.webp'), reverse=True)]
fl_meta = {f['f'][:-4]: f for f in json.load(open(B / 'raw/flyers.json', encoding='utf8'))}
aff_html = ''.join(f'<figure style="margin:0"><button data-lb="{{{{R}}}}assets/afiches/{p.name}" aria-label="Ampliar afiche"><img src="{{{{R}}}}assets/afiches/{p.name}" alt="Afiche de {esc(re.sub(r"\s+", " ", fl_meta.get(p.stem, {}).get("t", "carrera"))[:70])}" loading="lazy" decoding="async"></button><figcaption>{p.stem[:4]}</figcaption></figure>' for p in aff)
fotos = f'''<section class="ph"><div class="wrap"><h1>Fotos</h1><p class="lead">Una selección de nuestro Instagram. Hay {len(aff)} afiches más abajo: cada carrera tiene el suyo.</p><p style="margin-top:18px"><a class="btn" href="{IG}" rel="noopener">Más en @kminfinito</a></p></div></section>
<section class="sec" style="padding-top:clamp(20px,3vw,40px)"><div class="wrap pgrid">{grid}</div></section>
<section class="sec soft"><div class="wrap"><h2 style="margin-bottom:22px">El muro de los afiches</h2><div class="pgrid af">{aff_html}</div></div></section>'''
page('fotos/index.html', 'Fotos y afiches de las carreras | Kilómetro Infinito', 'Fotos de largadas, barro y podios, y el archivo de afiches de las carreras cronometradas por KMI.', fotos, 'fotos/')

# ---------------------------------------------------------------- Inscripción
PASOS = [('Completá el formulario', 'Elegís la carrera en el calendario y mandás tus datos. Revisalos bien, y poné un mail que funcione.'), ('Te respondemos por mail', 'Con la confirmación y el número de cuenta. Contestamos de lunes a viernes, a las 13 y a las 20. Por lo general en menos de 24 horas.'), ('Pagá y mandá el comprobante', 'Sin comprobante por mail no estás anotado. Te avisamos cuando lo recibimos, siempre por mail.'), ('Buscate en la lista', 'La planilla de inscriptos queda a la vista en la página de la carrera.')]
insc = f'''<section class="ph"><div class="wrap"><h1>Cómo inscribirme</h1><p class="lead">Son cuatro pasos. El precio sube por tramos, así que conviene no dejarlo para último momento.</p></div></section>
<section class="sec"><div class="wrap scene"><div class="pic rv">{img('corredoras-con-numero-mar-de-cobo')}</div><div><ol class="say" style="list-style:none">{''.join(f'<li class="rv"><h3>{a}</h3><p>{b}</p></li>' for a, b in PASOS)}</ol><a class="btn" href="{{{{R}}}}calendario/">Elegir carrera</a></div></div></section>
<section class="sec soft"><div class="wrap"><h2 style="margin-bottom:20px">Preguntas</h2>{''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in FAQ)}</div></section>'''
page('inscripcion/index.html', 'Cómo inscribirme en una carrera de KMI | Paso a paso', 'Formulario, respuesta por mail, pago y comprobante: cómo inscribirte en las carreras con el crono de Kilómetro Infinito y a quién preguntarle.', insc, schema=[faq_schema(FAQ)])

# ---------------------------------------------------------------- Contacto
cont = f'''<section class="ph"><div class="wrap"><h1>Contacto</h1><p class="lead">Adrián Eduardo Poó, Ayacucho, provincia de Buenos Aires.</p></div></section>
<section class="sec"><div class="wrap two"><div><a class="mail" style="font-size:clamp(1.4rem,3.7vw,4rem)" href="mailto:{MAIL}">{MAIL}</a><dl class="facts" style="margin-top:28px"><dt>WhatsApp y teléfono</dt><dd><a href="https://wa.me/{WA}">(0249) 15-455-1251</a></dd><dt>Instagram</dt><dd><a href="{IG}" rel="noopener">@kminfinito</a></dd><dt>Facebook</dt><dd>Adrián Eduardo Poó (Kilómetro Infinito)</dd><dt>Inscripción en persona</dt><dd>Bikes Amigorena, Colón 7199, Mar del Plata</dd></dl><div class="btns" style="margin-top:24px"><a class="btn" href="{{{{R}}}}cronometraje/#presupuesto">Pedir presupuesto</a><a class="btn line" href="{{{{R}}}}calendario/">Inscribirme en una carrera</a></div></div>{img('adrian-poo-sombrero-locucion')}</div></section>'''
page('contacto/index.html', 'Contacto | Kilómetro Infinito, Ayacucho', 'Teléfono, WhatsApp, mail e Instagram de Kilómetro Infinito (KMI), cronometraje de carreras en Ayacucho, provincia de Buenos Aires.', cont, 'contacto/')
page('p/contacto.html', 'Contacto', 'Contacto', '<section class="ph"><div class="wrap"><h1 class="mid"><a href="{{R}}contacto/">Contacto</a></h1></div></section><script>location.replace("../contacto/")</script>', noindex=True, sitemap=False)
page('p/calendario-de-competencias-2025-con-el.html', 'Calendario', 'Calendario', '<section class="ph"><div class="wrap"><h1 class="mid"><a href="{{R}}calendario/">Calendario</a></h1></div></section><script>location.replace("../calendario/")</script>', noindex=True, sitemap=False)


# ---------------------------------------------------------------- Páginas viejas de solo texto y posteos
def text_of(c):
    t = re.sub(r'<(style|script|xml)[^>]*>.*?</\1>|<!--.*?-->', '', c, flags=re.S | re.I)
    t = re.sub(r'<(br|/p|/div|/tr|/li|/h\d)[^>]*>', '\n', t, flags=re.I)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t)).replace('\xa0', ' ')
    return [re.sub(r'\s+', ' ', x).strip() for x in t.split('\n') if x.strip()]


have_tables = {p.stem for p in (D / 'results').glob('*.json')}
txt_pages = 0
for f in glob.glob(str(B / 'raw/pages/*.json')):
    p = json.load(open(f, encoding='utf8'))
    slug = p['u'].split('/p/')[-1].replace('.html', '')
    if slug in have_tables:
        continue
    lines = text_of(p['c'])
    if not lines:
        lines = ['Esta página no tiene contenido para mostrar.']
    title = re.sub(r'\s+', ' ', p['t']).strip()
    b = f'<section class="ph"><div class="wrap"><p class="crumbs"><a href="{{{{R}}}}campeonatos/">Campeonatos</a> · <a href="{{{{R}}}}resultados/">Resultados</a></p><h1 class="mid">{esc(title)}</h1></div></section><section class="sec"><div class="wrap prose">' + ''.join(f'<p>{esc(x)}</p>' for x in lines[:400]) + '</div></section>'
    page(f'p/{slug}.html', title, f'{title}. Kilómetro Infinito.', b, 'campeonatos/')
    txt_pages += 1

posts = json.load(open(B / 'raw/posts_km.json', encoding='utf8'))
ev_by_post = {e['post']: e for e in E if e.get('post')}
fl_by = {}
for x in json.load(open(B / 'raw/flyers.json', encoding='utf8')):
    fl_by.setdefault((x['d'], x['t']), x['f'])
arch = []
for e in posts:
    u = [l['href'] for l in e['link'] if l['rel'] == 'alternate'][0].split('kilometroinfinito.com.ar/')[-1]
    t = re.sub(r'\s+', ' ', e['title']['$t']).strip() or 'Publicación'
    d = e['published']['$t'][:10]
    ev = ev_by_post.get(u)
    if ev:
        first = ev['pages'][0]['slug']
        b = f'<section class="ph"><div class="wrap"><h1 class="mid">{esc(ev["name"])}</h1><p class="lead"><a href="{{{{R}}}}p/{first}.html">Ver la clasificación</a></p></div></section><script>location.replace("{"../../p/" + first + ".html"}")</script>'
        page(u, ev['name'], f'Clasificación de {ev["name"]}.', b, noindex=True, sitemap=False)
        continue
    lines = text_of(e['content']['$t'])
    fl = fl_by.get((d, e['title']['$t']))
    pic = flyer(fl, t) if fl else ''
    b = f'<section class="ph"><div class="wrap"><p class="crumbs"><a href="{{{{R}}}}archivo/">Archivo</a></p><h1 class="mid">{esc(t)}</h1><p class="lead">{fdate(d)}</p></div></section><section class="sec"><div class="wrap two"><div class="prose">' + ''.join(f'<p>{esc(x)}</p>' for x in lines[:500]) + f'</div>{pic}</div></section>'
    page(u, t, f'{t}. Publicado por Kilómetro Infinito el {fdate(d)}.', b, 'resultados/', noindex=not re.search(r'clasif|historia', t, re.I))
    arch.append((d, t, u))
arch.sort(reverse=True)
page('archivo/index.html', 'Archivo de KMI, 2010 a 2021 | Kilómetro Infinito', 'Los primeros años de Kilómetro Infinito: crónicas, fotos y clasificaciones publicadas en el blog desde 2010.',
     f'<section class="ph"><div class="wrap"><h1>Archivo</h1><p class="lead">Lo que fuimos publicando desde 2010: crónicas, avisos y clasificaciones de antes de que tuvieran su propia tabla.</p></div></section><section class="sec"><div class="wrap"><ul class="rank" style="columns:1">' + ''.join(f'<li><a href="{{{{R}}}}{u}">{esc(t)}<span>{fdate(d)}</span></a></li>' for d, t, u in arch) + '</ul></div></section>', 'resultados/')

# ---------------------------------------------------------------- Técnicos
(SITE / 'robots.txt').write_text(('User-agent: *\nDisallow: /\n' if NOINDEX else 'User-agent: *\nAllow: /\nDisallow: /corredor/\n') + f'Sitemap: {DOMAIN}/sitemap.xml\n', encoding='utf8')
(SITE / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{DOMAIN}{u}</loc></url>' for u in written) + '</urlset>', encoding='utf8')
(SITE / 'llms.txt').write_text(f'''# Kilómetro Infinito (KMI)
Cronometraje, clasificación y locución de carreras de mountain bike, rural bike, duatlón y running. Ayacucho, provincia de Buenos Aires, Argentina. Desde 2006.
Publicamos {S['events']} clasificaciones y {miles(S['results_unique'])} resultados de {miles(S['runners'])} corredores en {S['places']} localidades.
- Calendario e inscripción: {DOMAIN}/calendario/
- Resultados: {DOMAIN}/resultados/
- Campeonatos: {DOMAIN}/campeonatos/
- Cronometraje para organizadores: {DOMAIN}/cronometraje/
- Contacto: {MAIL}, (0249) 15-455-1251
''', encoding='utf8')
(SITE / '.nojekyll').write_text('', encoding='utf8')
page('404.html', 'Página no encontrada | Kilómetro Infinito', 'No encontramos esa página.', '<section class="ph"><div class="wrap"><h1>Se salió del circuito</h1><p class="lead">Esa página no está. Buscá tu nombre o andá a los resultados.</p>' + finder('nf') + '<p style="margin-top:20px"><a class="btn" href="/kilometro-infinito-website/resultados/">Resultados</a></p></div></section>', noindex=True, sitemap=False)
f404 = SITE / '404.html'
f404.write_text(f404.read_text(encoding='utf8').replace('<head>', '<head><base href="/kilometro-infinito-website/">', 1), encoding='utf8')
print('tablas', count_p, 'texto', txt_pages, 'archivo', len(arch), 'sitemap', len(written))
