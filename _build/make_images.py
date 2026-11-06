"""Procesa fotos de IG y afiches: recorta bandas negras de historias, mismo tratamiento de color, nombres descriptivos."""
import glob, os, json, pathlib
from PIL import Image, ImageEnhance, ImageOps
B = pathlib.Path(__file__).parent
SITE = B.parent
OUT = SITE / 'assets' / 'img'
FLY = SITE / 'assets' / 'afiches'
OUT.mkdir(parents=True, exist_ok=True)
FLY.mkdir(parents=True, exist_ok=True)

# indice IG -> (nombre de archivo, texto alternativo)
P = {
 1: ('corredoras-con-numero-mar-de-cobo', 'Corredoras con su número en el pecho antes de la largada de Mar de Cobo Corre'),
 2: ('saludo-bajo-arco-largada-mar-de-cobo', 'Corredora saluda frente al arco rojo de largada en Mar de Cobo'),
 3: ('largada-running-arco-rojo', 'Largada de running bajo el arco inflable rojo, con el pelotón saliendo'),
 4: ('corredores-reunidos-previa', 'Corredores reunidos en el pasto antes de la carrera'),
 6: ('podio-running-mar-de-cobo', 'Podio de la carrera con las ganadoras arriba del cajón'),
 7: ('corredoras-con-premios', 'Tres corredoras muestran las bolsas de premios'),
 9: ('operador-crono-notebook', 'Operador de KMI trabajando en la notebook, en la cabina de cronometraje'),
 12: ('adrian-poo-sombrero-locucion', 'Adrián Poó, con su sombrero, en la locución junto al arco de llegada'),
 13: ('pelotón-running-en-la-largada', 'Pelotón de corredores esperando la largada detrás de las vallas'),
 14: ('corredora-de-espaldas-remera', 'Corredora de espaldas con gorra mirando la llegada'),
 15: ('pelotón-mtb-camino-tierra', 'Pelotón de mountain bike en un camino de tierra con árboles al fondo'),
 16: ('podio-general-cajon', 'Corredores agrupados en el podio al aire libre'),
 19: ('arco-negro-llegada-camino', 'Arco negro de llegada al final de un camino claro, con público a los costados'),
 21: ('adrian-poo-selfie-sombrero', 'Adrián Poó con el sombrero, en el predio de una carrera'),
 23: ('corredoras-sonrientes-podio', 'Corredoras sonrientes con sus medallas'),
 24: ('corredora-tras-llegar', 'Corredora parada en el pasto después de cruzar la meta'),
 25: ('equipo-organizador-con-corredor', 'Grupo de organizadores y un ciclista posando juntos'),
 28: ('ciclistas-esperando-largada', 'Ciclistas esperando en la línea de largada'),
 31: ('ciclista-remera-colorida', 'Ciclista con remera colorida sostiene su bicicleta en el pasto'),
 34: ('ciclistas-camino-campo-cielo', 'Ciclistas en un camino de campo bajo un cielo azul'),
 35: ('premiacion-frente-carpa', 'Premiación frente a la carpa del organizador'),
 36: ('corredores-carpa-cielo-azul', 'Corredores frente a la carpa, con cielo azul y nubes'),
 37: ('dos-ciclistas-camino', 'Dos ciclistas parados con sus bicicletas en un camino de tierra'),
 39: ('ciclista-en-el-pasto', 'Ciclista avanzando por un tramo de pasto'),
 42: ('ciclista-sonrie-con-casco', 'Ciclista sonriendo con casco y anteojos'),
 44: ('ciclistas-esperando-entre-arboles', 'Ciclistas esperando entre los árboles antes de largar'),
 45: ('sendero-verde-arco-al-fondo', 'Sendero verde de pasto con el arco de meta al fondo'),
 58: ('eucaliptos-curva-mtb', 'Curva de tierra entre eucaliptos enormes durante la carrera'),
 59: ('ciclista-entre-eucaliptos', 'Ciclista inclinado en la curva entre eucaliptos'),
 60: ('ciclista-barro-arco-negro', 'Ciclista entrando en el barro con el arco negro detrás'),
 63: ('ciclista-barro-bosque-rosa', 'Ciclista con remera rosa en un sendero embarrado del bosque'),
 64: ('ciclista-barro-bosque', 'Ciclista con casco blanco atravesando el barro en el bosque'),
 65: ('largada-mtb-arco-negro-pelotón', 'Pelotón de mountain bike bajo el arco negro, listo para largar'),
 67: ('adrian-poo-sombrero-carpa', 'Adrián Poó se acomoda el sombrero debajo de la carpa amarilla'),
 86: ('arco-bienvenidos-rojo-ciclistas', 'Ciclistas pasando bajo el arco rojo de bienvenida'),
 88: ('ciclistas-sol-pasto', 'Ciclistas concentrados al sol en el pasto'),
 89: ('ciclistas-frente-arco-rojo', 'Ciclistas con sus bicicletas frente al arco rojo'),
 90: ('copas-mesa-premios', 'Mesa con las copas y trofeos de la premiación'),
 91: ('ciclista-desde-el-casco', 'Vista desde el casco: un ciclista avanzando por el campo'),
 92: ('bicicleta-roja-al-sol', 'Bicicleta roja apoyada, al sol'),
 103: ('llegada-arco-naranja-gente', 'Público y corredores frente al arco naranja de llegada'),
 104: ('recta-final-arco-naranja', 'Recta final de pasto hacia el arco naranja'),
 105: ('curva-cinta-pasto', 'Curva de pasto marcada con cinta, con un ciclista a lo lejos'),
 108: ('bicicleta-roja-detalle', 'Detalle de una bicicleta roja de carrera'),
 109: ('carpa-azul-ciclistas', 'Ciclistas junto a la carpa azul de la organización'),
 110: ('predio-desde-arriba-arco-rojo', 'El predio visto desde arriba, con el arco rojo y las vallas'),
 112: ('duatleta-corriendo-numero', 'Duatleta corriendo con anteojos espejados y el número en la cintura'),
 113: ('ruta-banderas-azules', 'Ruta con banderas azules en los costados, esperando a los corredores'),
 116: ('ciclistas-en-grupo-bosque', 'Grupo de ciclistas en un camino de tierra del bosque'),
 117: ('ciclistas-largada-bosque', 'Ciclistas en la largada de un camino del bosque'),
 124: ('ciclistas-camino-seco', 'Ciclistas en un camino seco de campo'),
}


def debar(im):
    """Saca bandas negras de las historias de Instagram."""
    g = im.convert('L')
    w, h = g.size
    top = 0
    while top < h // 2 and sum(g.crop((0, top, w, top + 1)).get_flattened_data()) / w < 14:
        top += 2
    bot = h
    while bot > h // 2 and sum(g.crop((0, bot - 1, w, bot)).get_flattened_data()) / w < 14:
        bot -= 2
    return im.crop((0, top, w, bot))


def grade(im):
    im = ImageOps.autocontrast(im, cutoff=(0.4, 0.4))
    im = ImageEnhance.Contrast(im).enhance(1.06)
    return ImageEnhance.Color(im).enhance(1.06)


manifest = {}
for f in glob.glob(str(B / 'raw' / 'ig_sel' / 'kmi-ig-*.jpg')):
    i = int(os.path.basename(f)[7:10])
    if i not in P:
        continue
    name, alt = P[i]
    name = name.replace('ó', 'o').replace('ñ', 'n')
    im = grade(debar(Image.open(f).convert('RGB')))
    if name == 'largada-mtb-arco-negro-peloton':
        im = im.crop((0, 0, im.size[0], int(im.size[1] * .86)))
    w, h = im.size
    if max(w, h) > 2200:
        im.thumbnail((2200, 2200), Image.LANCZOS)
    w, h = im.size
    im.save(OUT / f'{name}.webp', quality=78, method=6)
    manifest[name] = {'alt': alt, 'w': w, 'h': h}
logo = Image.open(B / 'raw' / 'ig_sel' / 'kmi-logo-perfil.jpg').convert('RGB')
logo.save(OUT / 'logo-kmi.webp', quality=92)
logo.save(SITE / 'assets' / 'favicon.png')
json.dump(manifest, open(B / 'data' / 'photos.json', 'w', encoding='utf8'), ensure_ascii=False, indent=0)
print('fotos', len(manifest), sum(v['w'] >= 1000 for v in manifest.values()), 'grandes')

ev = json.load(open(B / 'data' / 'events.json', encoding='utf8'))
n = 0
for f in glob.glob(str(B / 'raw' / 'flyers' / '*.jpg')):
    try:
        im = Image.open(f).convert('RGB')
    except Exception:
        continue
    if max(im.size) < 400:
        continue
    im.thumbnail((1000, 1000), Image.LANCZOS)
    im.save(FLY / (os.path.basename(f)[:-4] + '.webp'), quality=72, method=6)
    n += 1
print('afiches', n)
