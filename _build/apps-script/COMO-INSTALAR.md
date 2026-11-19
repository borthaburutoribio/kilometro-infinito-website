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

## 1b. Carreras con planilla del organizador (opcional)
Hoy, cuando el organizador también anota gente, Adrián le arma una planilla de Drive, le pasa el link y después la baja. Eso sigue igual:
1. En "KMI - Preinscripciones" aparece sola la pestaña **Carreras**.
2. En la columna A pone el nombre de la carrera tal cual sale en la web (por ejemplo `Caminos de Luna`) y en la B, el link de la planilla que comparte con ese organizador.
3. Desde ese momento, los que se anotan por la web caen en esa misma planilla, en una pestaña aparte llamada **"Inscriptos por la web"**. Así no se mezclan con las columnas del organizador, y Adrián baja todo de un solo lugar.
4. Si una carrera no está en la lista, las inscripciones van a "KMI - Preinscripciones", a una pestaña con el nombre de la carrera.

Ojo: el organizador va a ver los datos de los inscriptos por la web (DNI, celular). El comprobante queda en el Drive de Adrián, y el organizador solo lo puede abrir si Adrián le da permiso.

Cada vez que alguien se anota por la web, a Adrián le llega un **mail de aviso** con los datos y el link al comprobante (se apaga poniendo `AVISAR_POR_MAIL = false`).

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
