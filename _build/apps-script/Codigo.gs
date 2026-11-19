/**
 * Kilómetro Infinito: inscripciones y fotos de la web.
 * Se pega en una planilla de Google de Adrián (Extensiones > Apps Script) y se publica como "App web".
 * Hace dos cosas:
 *  1. Recibe cada preinscripción de la web: guarda el comprobante en Drive y agrega una fila a la planilla.
 *  2. Le pasa a la web la lista de fotos de cada carrera, sacada de una carpeta de Drive.
 * No manda mails ni confirma pagos: eso lo sigue haciendo Adrián.
 */

const CARPETA_COMPROBANTES = 'KMI - Comprobantes';
const CARPETA_FOTOS = 'KMI - Fotos de carreras';
const MAX_MB = 9;
const COLUMNAS = ['Fecha', 'Estado', 'Apellido', 'Nombre', 'DNI', 'Nacimiento', 'Rama', 'Modalidad', 'Categoría', 'Monto', 'Celular', 'Mail', 'Ciudad', 'Equipo', 'Pareja o posta', 'Comprobante'];

function carpeta_(nombre, padre) {
  const it = padre ? padre.getFoldersByName(nombre) : DriveApp.getFoldersByName(nombre);
  return it.hasNext() ? it.next() : (padre ? padre.createFolder(nombre) : DriveApp.createFolder(nombre));
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function texto_(v, max) {
  return String(v == null ? '' : v).replace(/[\r\n\t]+/g, ' ').trim().slice(0, max || 120);
}

// ---------------------------------------------------------------- 1. Preinscripciones
function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    const d = JSON.parse(e.postData.contents);
    const obligatorios = ['carrera', 'nombre', 'apellido', 'dni', 'nac', 'cel', 'mail', 'categoria'];
    for (const k of obligatorios) if (!texto_(d[k])) return json_({ ok: false, error: 'Falta ' + k });
    if (!d.comprobante || !d.comprobante.data) return json_({ ok: false, error: 'Falta el comprobante' });
    const bytes = Utilities.base64Decode(d.comprobante.data);
    if (bytes.length > MAX_MB * 1048576) return json_({ ok: false, error: 'El comprobante pesa demasiado' });
    const tipo = /^(image\/(jpeg|png|webp|heic)|application\/pdf)$/.test(d.comprobante.type) ? d.comprobante.type : 'application/octet-stream';

    // El comprobante va a una carpeta por carrera (privada: solo la ve Adrián)
    const dni = texto_(d.dni, 12).replace(/\D/g, '');
    const nombreArchivo = `${texto_(d.apellido, 40)} ${texto_(d.nombre, 40)} - DNI ${dni} - ${Utilities.formatDate(new Date(), 'America/Argentina/Buenos_Aires', 'yyyy-MM-dd HH.mm')}`;
    const dir = carpeta_(texto_(d.carrera, 80), carpeta_(CARPETA_COMPROBANTES));
    const archivo = dir.createFile(Utilities.newBlob(bytes, tipo, nombreArchivo));

    // Una pestaña por carrera
    const libro = SpreadsheetApp.getActiveSpreadsheet();
    const nombreHoja = texto_(d.carrera, 90);
    let hoja = libro.getSheetByName(nombreHoja);
    if (!hoja) {
      hoja = libro.insertSheet(nombreHoja);
      hoja.appendRow(COLUMNAS);
      hoja.setFrozenRows(1);
      hoja.getRange(1, 1, 1, COLUMNAS.length).setFontWeight('bold');
    }
    hoja.appendRow([
      new Date(), 'Pendiente', texto_(d.apellido, 60), texto_(d.nombre, 60), dni, texto_(d.nac, 10), texto_(d.rama, 12),
      texto_(d.modalidad, 12), texto_(d.categoria, 40), Number(d.monto) || '', texto_(d.cel, 30), texto_(d.mail, 80),
      texto_(d.ciudad, 60), texto_(d.equipo, 60), texto_(d.pareja, 120), archivo.getUrl()
    ]);
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: 'No se pudo guardar' });
  } finally {
    lock.releaseLock();
  }
}

// ---------------------------------------------------------------- 2. Fotos por carrera
// Adrián crea, dentro de "KMI - Fotos de carreras", una carpeta por carrera (ej.: "2026-11-22 Vuelta a Coronel Vidal")
// y la comparte como "Cualquier persona con el enlace puede ver". La web muestra las carpetas compartidas.
function doGet(e) {
  const p = (e && e.parameter) || {};
  if (p.fotos === 'lista') {
    const cache = CacheService.getScriptCache(), c = cache.get('lista');
    if (c) return json_(JSON.parse(c));
    const raiz = carpeta_(CARPETA_FOTOS), out = [];
    const it = raiz.getFolders();
    while (it.hasNext()) {
      const f = it.next();
      if (f.getSharingAccess() !== DriveApp.Access.ANYONE_WITH_LINK && f.getSharingAccess() !== DriveApp.Access.ANYONE) continue;
      const fs = f.getFiles(); let n = 0, tapa = '';
      while (fs.hasNext()) { const x = fs.next(); if (!/^image\//.test(x.getMimeType())) continue; if (!tapa) tapa = x.getId(); n++; }
      if (n) out.push({ id: f.getId(), nombre: f.getName(), tapa: tapa, n: n });
    }
    out.sort((a, b) => b.nombre.localeCompare(a.nombre));
    cache.put('lista', JSON.stringify(out), 600);
    return json_(out);
  }
  if (p.fotos) {
    const f = DriveApp.getFolderById(p.fotos);
    if (f.getSharingAccess() !== DriveApp.Access.ANYONE_WITH_LINK && f.getSharingAccess() !== DriveApp.Access.ANYONE) return json_([]);
    const ids = [], it = f.getFiles();
    while (it.hasNext()) { const x = it.next(); if (/^image\//.test(x.getMimeType())) ids.push({ id: x.getId(), nombre: x.getName() }); }
    ids.sort((a, b) => a.nombre.localeCompare(b.nombre));
    return json_({ nombre: f.getName(), fotos: ids.map(x => x.id) });
  }
  return json_({ ok: true, app: 'KMI' });
}
