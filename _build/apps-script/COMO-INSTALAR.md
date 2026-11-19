# Cómo se conecta la inscripción y las fotos (una sola vez, con Adrián)

Todo queda en la cuenta de Google de **Adrián**: la planilla, los comprobantes y las fotos. No se paga nada. Lleva unos 15 minutos por videollamada.

## 1. La planilla de preinscripciones
1. Adrián entra a Google Drive y crea una planilla nueva: **"KMI - Preinscripciones"**.
2. En la planilla: **Extensiones → Apps Script**.
3. Borra lo que aparece y pega todo el archivo `Codigo.gs` de esta carpeta. Guarda (ícono del disquete).
4. **Implementar → Nueva implementación → tipo "Aplicación web"**:
   - Ejecutar como: **yo** (Adrián)
   - Quién tiene acceso: **cualquier usuario**
5. Google le pide permiso para usar su Drive y su planilla: lo acepta **él**.
6. Copia la **URL de la aplicación web** (termina en `/exec`) y te la pasa.

## 2. En la web (lo hago yo)
- Pego la URL en `_build/build.py`, en `INSC_URL`, y pongo el alias, el CBU y el titular reales en `PAGO`.
- Regenero la web y pruebo una inscripción de punta a punta.

## 3. Cómo lo usa Adrián después
- **Cada preinscripción** aparece en una pestaña con el nombre de la carrera, con estado "Pendiente" y el link al comprobante (carpeta "KMI - Comprobantes").
- Él revisa el pago, cambia el estado a "Confirmado" y confirma al corredor como hoy. Después lo pasa a la lista de inscriptos pública de siempre.
- **La planilla de preinscripciones es privada**: tiene DNI y teléfonos. La lista pública tiene que mostrar solo nombre y categoría.

## 4. Fotos de cada carrera
1. En su Drive aparece la carpeta **"KMI - Fotos de carreras"** (se crea sola la primera vez que alguien entra a Fotos en la web).
2. Por cada carrera crea una carpeta adentro con fecha y nombre, por ejemplo `2026-11-22 Vuelta a Coronel Vidal`, y sube las fotos.
3. Comparte esa carpeta: **Compartir → Cualquier persona con el enlace → Lector**.
4. En unos 10 minutos la carrera aparece sola en la página Fotos de la web. Nadie tiene que tocar la web.

Las fotos quedan guardadas en su Drive (15 GB gratis), no en la web, así que la web no se pone lenta. Si se llena el Drive, se puede pasar a Google One (unos USD 2 por mes por 100 GB) o borrar carreras viejas.
