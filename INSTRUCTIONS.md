# Nombre: "Gestión de Proyectos Casinos de Chile"

# Actores
* Agente de asistencia conceptual para el desarrollo. Para esta versión es un agente openclaw llamado Perico
* Agente de desarrollo de código. Para esta versión es Antigravity

# Requerimiento

Preparar una app tipo HTML para usar con cualquier buscador para monitorear el avance en los distintos proyectos del área de proyectos de la empresa Casinos de Chile SpA.

# Definiciones generales

## Persistencia de datos, uso multiusuario y despliegue

### Fuentes de código y responsabilidades

La carpeta de Google Drive de la aplicación es el área de trabajo compartida de Antigravity y Perico.
GitHub es donde se guarda el repositorio y el código final aprobado
la VPS es el entorno de producción

El flujo obligatorio es:

**Antigravity modifica Drive → Perico revisa Drive → Antigravity hace commit/push → Perico hace verificación final en github → Perico actualiza la VPS → verificación en producción**

Roles:

* **Antigravity:** modifica los archivos de trabajo en Drive y prepara el commit/push.
* **Perico:** revisa directamente los archivos actuales de Drive antes del push, actualiza la VPS después de la aprobación y verifica la producción.
* **GitHub:** repositorio versionado; no implica que el cambio esté desplegado.
* **VPS:** entorno real de producción.

Los cambios hechos en Drive, en un workspace local o en GitHub no se consideran desplegados hasta que Perico confirme el contenido dentro del contenedor Docker de producción.

### Producción actual

La aplicación productiva funciona en la VPS con:

* Ruta de trabajo: `/home/perico/enjoy`
* Contenedor de aplicación: `enjoy-app-1`
* Servicio: Streamlit
* Base runtime: PostgreSQL
* Variable de conexión: `ENJOY_DB_DSN`
* Tabla: `enjoy_records` con registros JSONB

El despliegue requiere copiar o actualizar los archivos aprobados en `/home/perico/enjoy`, ejecutar `docker compose up -d --build app` y verificar hashes, logs, estado del contenedor y comportamiento funcional.

### Google Sheets de trabajo

La planilla `BD Consola Enjoy - central` de Google Sheets se utiliza para desarrollo, validación controlada o respaldo, pero no como base de producción. Es una fuente de trabajo e intercambio manual de datos:

ID:

`1dpA2Nnk9dZ_NVkhJD1HHRBN4CH6Ry8bzm2Iuf_oXV8Y`

No es la base runtime de la VPS. Si se editan tareas en Google Sheets, la sincronización hacia PostgreSQL debe ejecutarse explícitamente y validarse antes de usar esos datos en producción.
Las pruebas locales conectadas a Google Sheets deben limitarse, porque las lecturas y recargas pueden consumir rápidamente el rate limit.

Reglas obligatorias:

* Las pruebas que modifiquen datos deben realizarse en la VPS, después de respaldar PostgreSQL y autorizar explícitamente la prueba.
* Un push de código no debe modificar ni reemplazar la base de datos.
* Nunca se debe sobrescribir el adaptador PostgreSQL de la VPS con el adaptador de Google Sheets.
* PostgreSQL `enjoy_records` es la fuente runtime de producción.
* `localStorage` no debe ser la fuente principal de datos.
* `localStorage` sólo puede usarse como caché temporal del navegador.
* Al iniciar o refrescar la app, siempre debe cargar información desde la base central.
* Al crear, editar, terminar o eliminar una tarea o proyecto en producción, el cambio debe guardarse inmediatamente en PostgreSQL `enjoy_records`.
* Los cambios hechos por un usuario deben quedar disponibles para otros usuarios al abrir o refrescar la app.
* `data.js` puede usarse únicamente como semilla inicial si la base central está vacía.
* `data.js` no debe considerarse base viva de trabajo.
* `carga_masiva.xlsx` debe usarse sólo como plantilla o mecanismo de importación manual.
* La descarga/exportación de base de datos debe exportar la información vigente desde PostgreSQL `enjoy_records`.

### Credenciales y secrets

En producción VPS, la conexión a PostgreSQL se realiza mediante `ENJOY_DB_DSN` inyectada por Docker.

Importante:

* El archivo `.streamlit/secrets.toml` local sirve sólo para desarrollo local.
* El archivo `secrets.toml` no debe subirse a GitHub.
* No se debe asumir que Streamlit Cloud es el entorno productivo actual.
* La cuenta usada por `gog` puede leer y actualizar la Google Sheet de trabajo, pero esa hoja no reemplaza la base runtime PostgreSQL.

### Arranque correcto de la app

La app no debe abrirse directamente como `index.html` para uso real, porque en ese modo:

* no corre Streamlit,
* no se ejecuta `app.py`,
* no se ejecuta `db_manager.py`,
* no se lee la configuración de producción,
* no se conecta a PostgreSQL,
* los cambios pueden quedar sólo en `localStorage`.

Para desarrollo local, el arranque correcto debe ser:

```bat
@echo off
cd /d "%~dp0"
streamlit run app.py
```

### Confirmación de guardado

La app debe informar explícitamente el estado de guardado con mensajes simples para el usuario final:

* Si guarda correctamente: **“Guardado”**
* Si falla: **“Error: no se pudo guardar”**

Si la app se abre sin conexión a Streamlit o sin conexión efectiva a la base central, debe mostrar una advertencia visible y no dar por guardados los cambios.


## Formatos y unidades

Reglas de fomatos y unidades
* Todas las fechas que aparezcan en la interfaz de usuario deben aparecer en formato DD/MM/AAAA.


## Empresa

Casinos de Chile es una empresa que administra Casinos y Hoteles de la cadena Enjoy que cuenta con 5 complejos turísticos, llamados internamente "Unidades de Negocios" o "Unidades.

## Unidades

Los complejos turísticos o Unidades son:

* Rinconada
* Pucón
* Viña
* Coquimbo
* Chiloé
* Transversales

Las respectivas abreviaciones son:

* RI
* PU
* VI
* CQ
* CH
* TR

## Campos

Para el desarrollo de la app se contará con los siguientes datos para cada tarea:

proyecto\_id: código único de identificación del proyecto. La estructura es AAAA\_UN\_NNN donde AAAA es el año, UN es la abreviación de la Unidad y NNN es el número correlativo que sigue al último creado.

unidad\_nombre: Nombre de la Unidad de Negocio

proyecto\_nombre: Nombre del Proyecto

proyecto\_estado: Estado actual del proyecto. Puede ser "por iniciar", "en desarrollo", "en construcción", "detenido", "terminado", "eliminado"

proyecto\_descripcion: Descripción del proyecto.

tarea\_id: código único de identificación de la tarea. La estructura es AAAA\_UN\_NNN\_TTT donde AAAA\_UN\_NNN es el id del proyecto y TTT es el número correlativo de la tarea que sigue a la última creada.

tarea\_nombre: nombre abreviado de la tarea

tarea\_descripcion: descripción de la tarea

tarea\_responsable: Iniciales del responsable de la Gerencia de Proyectos

tarea\_estado: Estado actual de la tarea. Puede ser "por iniciar", "en desarrollo", "detenida", "terminada", "eliminada"

tarea\_contraparte: Nombre del responsable por parte de la unidad

tarea\_pct: porcentaje de avance en la tarea

fecha\_legacy: Corresponde a fechas legacy de las minutas en word utilizadas hasta implementación de la app, que serán traspasadas desde  un archivo de carga masiva o ajustadas manualmente en la tabla de "Proyectos Admin". Son sólo fechas referenciales que representan el inicio de la tarea constatada en reportes anteriores.

con\_alerta: La tarea debe ser considerada prioritaria y requiere atención especial

tarea\_fecha\_creacion: Se establece al momento de crear una tarea. Su fin es sólo estadístico y no participa de informes, fichas o formulario. Sólo se puede editar en "Proyectos Admin" 

fecha\_inicio\_proy: Corresponde a la fecha de inicio proyectada de una tarea.

fecha\_inicio\_real: Corresponde a la fecha de inicio real de una tarea. Editable sólo en Admin; ignorada en filtros, cálculos, fichas y formularios.

fecha\_fin\_proy: Corresponde a la fecha de fin proyectada de una tarea.

fecha\_fin\_real: Corresponde a la fecha de fin real de una tarea. automática en operación normal; editable sólo como corrección administrativa en Admin. Si al momento de cambiar de estado de "en desarrollo" a "terminada" o a "eliminada" no tiene valor, se debe establecer la fecha del momento del cambio. Si fecha_fin_real existe, no se debe modificar salvo una acción explícita de corrección administrativa. El usuario no debe ingresar manualmente fecha_fin_real. Si una tarea cambia desde "terminada" o "eliminada" a un estado activo, la aplicación debe limpiar fecha_fin_real, porque la tarea deja de estar cerrada.

### Definiciones de fechas:



## Usuarios

Los usuarios y sus características serán 3:

* CEO de Casinos de Chile SpA.:  Necesitará lograr una comprensión general pero precisa del avance en las tareas de los distintos proyectos de forma ágil. Dispone de poco tiempo para revisar y la simpleza será clave. Consultará sólo un dashboard.
* Subgerenta de Proyectos: No tiene experiencia con medios digitales, necesitará una app limpia y fácil de usar. Esto se traduce en que cada sección que este profesional consulte debe tener el mínimo de información. Además de visualizar las mismas secciones que el CEO, deberá poder crear y editar los proyectos en la misma consola.
* Jefe de Proyectos: Será el encargado de administrar la aplicación, haciendo el troubleshooting, cargando información y haciendo mejoras que vayan siendo necesarias.

La descripción de los usuarios busca detallar la experiencia que tienen para acotar la complejidad de las distintas secciones de la app.

## Colores

Los colores a utilizar para títulos, fondos de tarjetas y otros serán:
#C04F15 para títulos
#595959 Para subtítulos, listas y otros textos
#F6C6AD Para fondos
#F2F2F2 Para fondos

# Secciones

La app tendrá 4 secciones con sus respectivos botones en el panel lateral

1. Dashboard
2. Fecha de informe
3. Proyectos
4. Admin



El panel lateral no debe tener ningún título



## 1\. Dashboard

En la parte superior tendrá un título que será "Proyectos En Desarrollo" y al lado tendrá un menú desplegable para filtrar por unidad de negocio.

El cuerpo del Dashboard estará separado en 3 zonas del mismo ancho, cada zona con su título que serán los siguientes:

* "Unidad de Negocio"
* "Tareas en Curso
* "Alertas"



### Zona "Proyectos por Unidad de Negocio" en dashboard

Un listado de las unidades de negocio con proyectos activos. No debe incluir proyectos con estado "terminado" o "eliminado"
A la izquierda de cada elemento debe haber un botón un número que representa la cantidad de proyectos en curso para la unidad. El botón debe ser de color gris con el texto color blanco.
Bajo cada elemento debe ir un listado con los proyectos en curso. Al hacerle click a cada elemento de la lista genera el listado de tareas en la siguiente zona "Tareas en Curso"
Para proyectos que tengan tareas con campo en\_alerta con valor "si" agrega un semáforo en rojo.



### Zona "Tareas en Curso"

Un listado dinámico que se genera al hacer click a un proyecto de la zona "Proyectos por Unidad" mostrando una columna con el nombre de las tareas en curso del proyecto seleccionado con estado "por iniciar", "en desarrollo" o "detenida". No mostrar tareas en estado "terminada" o "eliminada". Cada ítem de la lista corresponde al nombre de la tarea del proyecto seleccionado en la zona "Proyectos por Unidad de Negocio". Cada ítem de la lista debe ser un vínculo a la ficha de la tarea. Junto a la columna de nombre de la tarea debe haber una columna con el responsable. Junto a la columna del responsable agregar una columna con un ícono de semáforo con las siguientes instrucciones:
color verde: tareas con tarea\_estado "en desarrollo" con "con\_alerta" en "no"
color amarillo: tareas con tarea\_estado "detenida" con "con\_alerta" en "no"

color rojo: tareas con tarea\_estado "en desarrollo", "detenida" o "por iniciar" que tengan "con\_alerta" en "si".


Al abrir la app las tareas de esta zona se deben ordenar en base a la fecha de creación de cada tarea, desde la más reciente a la más antigua.


### Zona "Avance Semanal"

Es un resumen de tareas relevantes para la semana correspondiente a la **Fecha de Informe** seleccionada por el usuario.

La semana se calcula tomando la semana calendario correspondiente a la **Fecha de Informe**.

La zona queda dividida en 3 subsecciones, una sobre la otra, en este orden:

1. **Tareas Creadas**
2. **Tareas Terminadas**
3. **Actualizar Fechas**

Si hay filtro de Unidad de Negocio activo en el Dashboard, el filtro debe aplicarse también a las tres subsecciones de **Avance Semanal**.

#### Tareas Creadas

Una tarea debe aparecer en **Tareas Creadas** sólo si cumple todos estos criterios:

* `fecha_inicio_proy` tiene valor.
* `fecha_inicio_proy` pertenece a la misma semana de la **Fecha de Informe**.
* `tarea_estado` es `"en desarrollo"` o `"detenida"`.
* `fecha_fin_real` no tiene valor

`tarea_fecha_creacion` no debe utilizarse para esta clasificación.


#### Tareas Terminadas

Una tarea debe aparecer en **Tareas Terminadas** sólo si cumple todos estos criterios:

* `tarea_estado` es `"terminada"` o `"eliminada"`.
* `fecha_fin_real` tiene valor.
* `fecha_fin_real` pertenece a la misma semana de la **Fecha de Informe**.

La clasificación semanal debe basarse en `fecha_fin_real`, no en `fecha_fin_proy`.

#### Actualizar Fechas

Esta subsección debe mostrar tareas que tengan inconsistencias o fechas incompletas que puedan afectar la lectura del avance semanal.

Deben aparecer en **Actualizar Fechas** las tareas que cumplan cualquiera de estos criterios:

- Tarea activa (`"por iniciar"`, `"en desarrollo"` o `"detenida"`) con `fecha_fin_proy` o `fecha_fin_real` informada.
- Tarea `"terminada"` o `"eliminada"` sin `fecha_fin_real`.
- Tarea activa o terminada sin `fecha_inicio_proy`.
- Tareas con `tarea_estado` `"terminada"` y `tarea_pct` con un valor distinto a 100.
- Tareas con `tarea_estado` `"en desarrollo"` o `"detenida"` y `tarea_pct` con un valor igual a 100.
- Fechas incompatibles con el estado actual de la tarea.

`fecha_inicio_real` debe ser ignorada en filtros, cálculos, fichas y formularios.


La subsección **Actualizar Fechas** es una alerta de calidad de datos. Su objetivo es indicar qué tareas requieren completar o corregir fechas antes de interpretar el avance semanal.

#### Semáforo en Avance Semanal

A la derecha del nombre de la tarea, agregar una columna con ícono de semáforo con los mismos parámetros que en **Tareas en Curso**:

* Color verde: tareas con `tarea_estado` `"en desarrollo"` y `con_alerta` en `"no"`.
* Color amarillo: tareas con `tarea_estado` `"detenida"` y `con_alerta` en `"no"`.
* Color rojo: tareas con `tarea_estado` `"en desarrollo"`, `"detenida"` o `"por iniciar"` que tengan `con_alerta` en `"si"`.

## 2\. Fecha de Informe

La Fecha de Informe determina la semana calendario utilizada por “Avance Semanal”.

- La fecha debe mostrarse al usuario como DD/MM/AAAA.
- Internamente debe normalizarse como YYYY-MM-DD.
- Al iniciar completamente la aplicación debe establecerse en la fecha actual.
- Debe conservarse al navegar entre dashboards, proyectos, tareas y subsecciones.
- switchView() y los botones de navegación no deben modificarla.
- Debe existir un botón compacto, sólo con el ícono de recarga, que restablezca la Fecha de Informe al día actual.
- El botón debe tener tooltip y etiqueta accesible: “Restablecer fecha al día actual”.
- La fecha sólo debe cambiar al día actual al recargar completamente la aplicación o al presionar dicho botón.
- El campo de ingreso de fecha debe tener un ancho compacto, suficiente para DD/MM/AAAA.



## 3\. Proyectos

Una tabla que contiene todos los proyectos que tengan estado\_proyecto "por iniciar", "en desarrollo", "en construcción", "detenido" y las tareas que tengan estado\_tarea  "por iniciar", "en desarrollo", "detenida" ordenados de la siguiente manera, con los respectivos campos entre paréntesis:



Columna 1: UN Negocios (unidad\_nombre)
Columna 2: Proyecto (proyecto\_nombre)
Columna 3: Nombre tarea (tarea\_nombre)
Columna 4: Descripción tarea (tarea\_descripcion), los textos en esta columna no deben tener más de 4 líneas.
Columna 5: Responsable (tarea\_responsable)
Columna 6: Estado (tarea\_estado), debe ser editable
Columna 7: Avance % (tarea\_pct), debe ser editable
Columna 8: Fecha inicio (proy) (fecha\_inicio\_proy),  debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 9: Fecha fin (proy) (fecha\_fin\_proy),  debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 10: En Alerta (selector "si/no" para definir con\_alerta)
Columna 11: Terminar (botón de check)
Columna 12: Borrar (botón de borrado, cambia el estado a "eliminada", con ícono)



Los encabezados deben estar fijos, sólo se debe poder desplazar la lista.



"Unidad Negocios" debe ser un link que abra la ficha de la unidad
"Proyecto" debe ser un link que abra la ficha del proyecto
"Nombre tarea" debe ser un link que abra la ficha de la tarea

No incluir el nombre del campo en los encabezados.
No incluir proyectos con proyecto\_estado "terminado" o "eliminado"
No incluir tareas con tarea\_estado "terminada" o "eliminada"
El color de todos los textos debe ser #595959

Junto al título de la sección debe haber un botón "Nuevo proyecto" y otro "Nueva tarea" que lleven a sus respectivos formularios.

Bajo la tabla debe aparecer un título que sea "Tareas terminadas o eliminadas" que despliegue una lista igual a la anterior pero para tareas con estado "terminada" o "eliminada". Se debe poder editar las tareas. Debe ser una sección desplegable bajo el título, o en el mismo título. Debe aparecer contraída.
A la derecha del este título pero pegado al margen derecho del listado debe haber un botón que diga "Volver" que lleve al dashboard.



Formulario de creación de "Nueva tarea"

Una tarjeta con los siguientes campos para llenar:

* unidad\_nombre: muestra un menú desplegable con las unidades
* proyecto\_nombre: muestra un menú desplegable con los proyectos en curso para "unidad\_nombre", con una opción "nuevo proyecto" que lleva al formulario de creacion de nuevo proyecto.
* tarea\_nombre
* tarea\_descripcion
* tarea\_responsable
* tarea\_contraparte
* tarea\_estado
* con\_alerta
* fecha\_inicio\_proy
* fecha\_fin\_proy

No debe incluir:

- fecha_inicio_real
- fecha_fin_real
- tarea_fecha_creacion, no se utiliza


Campos que se llenan automáticamente:

\- tarea\_id se crea automáticamente con las reglas establecidas antes

\- tarea\_estado se crea automáticamente en "en desarrollo", se debe poder editar en la ficha y en el formulario

\- fecha\_inicio\_proy se crea automáticamente con la fecha del día de la creación de la tarea, se debe poder editar en la ficha y en el formulario.

\- tarea\_pct se crea automáticamente en 0, se debe poder editar en la ficha y en el formulario

Al final, botón "Guardar" y "Descartar", uno al lado del otro.



Formulario de creación de "Nuevo proyecto"
Una tarjeta con los siguientes campos:

* unidad\_nombre: muestra un menú desplegable con las unidades

\- proyecto\_nombre

\- proyecto\_descripcion



Campos que se llenan automáticamente:

proyecto\_estado se crea automáticamente como "en desarrollo"
Al final, botón "Guardar" y "Descartar", uno al lado del otro.





## 4\. Admin

En esta sección se hará la administración de la app. Contará con las siguientes sub-secciones, las que se ordenarán a modo de lista con los respectivos títulos:

"Archivo de Carga Masiva"

junto al título debe tener un botón con un ícono que represente "download" que descarga un archivo en formato .xlsx llamado "carga\_masiva.xlsx". Debe mostrar una descripción que diga "descargue la plantilla para carga de datos".



El archivo .xlsx debe tener los siguientes encabezados, alineados con todos los campos usados por la app:

- proyecto\_id
- unidad\_nombre
- proyecto\_nombre
- proyecto\_estado
- proyecto\_descripcion
- tarea\_id
- tarea\_nombre
- tarea\_descripcion
- tarea\_responsable
- tarea\_estado
- tarea\_contraparte
- tarea\_pct
- tarea\_fecha\_creacion
- fecha\_legacy
- con\_alerta
- fecha\_inicio\_proy
- fecha\_inicio\_real
- fecha\_fin\_proy
- fecha\_fin\_real



"Carga Masiva"

junto al título debe tener un botón con un ícono que represente "upload". Debe tener una breve descripción que diga "seleccione archivo con base de datos"


"Descarga de Base de Datos"

descarga la base de datos en un archivo .xlsx ordenada en columnas con los mismos encabezados de "Carga Masiva"

"Proyectos Admin"

Esta subsección permite administrar directamente los registros existentes en la base de datos. Su objetivo es permitir la revisión, corrección y mantención de los datos principales de cada proyecto y sus tareas desde la consola, sin necesidad de editar manualmente el archivo base.

Debe mostrarse como una tabla editable con una fila por registro/tarea. La tabla debe incluir los siguientes campos:

- `borrado_permanente`: no corresponde a un campo de datos. En esta columna debe aparecer un botón de borrado que elimine de manera permanente de la base de datos la fila/registro correspondiente.
- `proyecto_id`: no editable. Identificador único del proyecto en la base de datos.
- `unidad_nombre`: editable. Unidad de Negocio a la que pertenece el proyecto.
- `proyecto_nombre`: editable. Nombre del proyecto.
- `proyecto_estado`: editable. Debe usar un selector desplegable con los estados válidos del proyecto.
- `proyecto_descripcion`: editable. Descripción general del proyecto.
- `tarea_id`: no editable. Identificador único de la tarea asociada.
- `tarea_nombre`: editable. Nombre de la tarea.
- `tarea_descripcion`: editable. Descripción de la tarea.
- `tarea_responsable`: editable. Responsable de la tarea.
- `tarea_estado`: editable. Debe usar un selector desplegable con los estados válidos de la tarea.
- `tarea_contraparte`: editable. Contraparte asociada a la tarea.
- `tarea_pct`: editable. Porcentaje de avance de la tarea.
- `tarea_fecha_creacion`: editable. Debe incluir un botón para desplegar un calendario.
- `fecha_legacy`: editable. Debe incluir un botón para desplegar un calendario.
- `con_alerta`: editable. Debe usar un selector con las opciones `"si"` y `"no"`.
- `fecha_inicio_proy`: editable. Debe incluir un botón para desplegar un calendario.
- `fecha_inicio_real`: editable sólo en Admin; ignorada en filtros, cálculos, fichas y formularios. Debe incluir un botón para desplegar un calendario.
- `fecha_fin_proy`: editable. Debe incluir un botón para desplegar un calendario.
- `fecha_fin_real`: editable. Debe incluir un botón para desplegar un calendario.

El botón de borrado permanente debe estar claramente diferenciado de otros botones de eliminación lógica. Su acción debe eliminar el registro/fila de forma definitiva desde la base de datos, no sólo cambiar su estado a `"eliminada"`. Antes de ejecutar el borrado permanente, la app debe solicitar confirmación al usuario.

# Fichas

## Ficha "Unidad de Negocio"

En la parte superior de la ficha debe haber un menú desplegable para seleccionar otras "Unidades de Negocio".
La ficha debe tener una tarjeta con fondo blanco con la siguiente información en texto grande:

* Unidad: (unidad\_nombre)
* Proyectos en curso: (suma de proyectos que estén en estado "por iniciar", "en desarrollo", "en construcción" o "detenido")
* Tareas en curso: (suma de tareas que estén en estado "por iniciar", "en desarrollo", o "detenida", suma sólo las tareas de la unidad)
* Tareas en alerta: (listado de tareas con\_alerta en "si")

Los títulos dentro de la tarjeta deben disponerse de modo que se vea una columna con los textos alineados a la izquierda y el contenido en otra columna con los textos alineados a la izquierda.



Luego bajo la tarjeta debe  haber una tabla que contiene todos los proyectos ordenados de la siguiente manera, con los respectivos campos entre paréntesis:
Columna 1: Proyecto (proyecto\_nombre)
Columna 2: Nombre tarea (tarea\_nombre)
Columna 3: Descripción tarea (tarea\_descripcion)
Columna 4: Responsable (tarea\_responsable)
Columna 5: Estado (tarea\_estado)
Columna 6: Porcentaje de avance (tarea\_pct)
Columna 7: Fecha inicio (proy) (fecha\_inicio\_proy), debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 8: Fecha fin (proy) (fecha\_fin\_proy), debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 9: En Alerta (selector "si/no" para definir con\_alerta)
Columna 10: Terminar (botón de check)
Columna 11: Borrar (botón de borrado, cambia el estado a "eliminada", con ícono)

"Unidad Negocios" debe ser un link que abra la ficha de la unidad
"Proyecto" debe ser un link que abra la ficha del proyecto. No mostrar proyectos que estén en estado "terminado" o "eliminado"
"Nombre tarea" debe ser un link que abra la ficha de la tarea. No mostrar tareas que estén en estado "terminada" o "eliminada".

Bajo la tabla debe aparecer un título que sea "Proyectos terminados o eliminados" que despliegue una lista igual a la anterior pero para proyectos con estado "terminado" o "eliminado".Debe ser una sección desplegable bajo el título, o en el mismo título. Debe aparecer contraída. A la derecha del este título pero pegado al margen derecho del listado debe haber un botón que diga "Volver" que lleve al dashboard.



## Ficha "Proyecto"

Junto al título de la sección debe haber un menú desplegable para seleccionar otros "Proyectos" de la Unidad correspondiente al proyecto de la ficha y un botón "Nueva tarea" que lleve a su respectivo formulario.

La ficha debe tener una tarjeta con fondo blanco con la siguiente información en texto grande:

* "Unidad de Negocio": (unidad\_nombre), debe ser un vínculo que lleve a la ficha de la unidad.
* "Proyecto": (proyecto\_nombre), debe mostrar sólo proyectos asociados a la unidad. debe ser editable
* "Estado del Proyecto": (proyecto\_estado), debe tener un menú desplegable con las opciones, que permita modificar el estado.
* "Tareas en curso": (cantidad de tareas, no mostrar tareas que estén en estado "terminada" o "eliminada". Cuenta sólo las tareas del proyecto)
* "Tareas en alerta": (listado de tareas con\_alerta en "si", cuenta sólo las tareas del proyecto)



Los títulos dentro de la tarjeta deben disponerse de modo que se vea una columna con los textos alineados a la izquierda y el contenido en otra columna con los textos alineados a la izquierda.



Luego bajo la tarjeta debe  haber una tabla que contiene todas las tareas del proyecto de ordenadas de la siguiente manera, con los respectivos campos entre paréntesis:

Columna 1: Nombre tarea (tarea\_nombre)
Columna 2: Descripción tarea (tarea\_descripcion)
Columna 3: Responsable (tarea\_responsable)
Columna 4: Estado (tarea\_estado)
Columna 5: Porcentaje de avance (tarea\_pct)
Columna 6: Contraparte (tarea\_contraparte)
Columna 7: Fecha inicio (proy) (fecha\_inicio\_proy), debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 8: Fecha fin (proy) (fecha\_fin\_proy), debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 9: En Alerta (selector "si/no" para definir con\_alerta)
Columna 10: Terminar (botón de check)
Columna 11: Borrar (botón de borrado, cambia el estado a "eliminada", con ícono)



"Unidad de Negocio" que aparece en la tarjeta debe ser un link que abra la ficha de la unidad
"Proyecto" que aparece en la tarjeta debe ser un link que abra la ficha del proyecto. No mostrar proyectos que estén en estado "terminado" o "eliminado"
"Nombre tarea" en el listado debe ser un link que abra la ficha de la tarea. No mostrar tareas que estén en estado "terminada" o "eliminada".

Bajo la tabla debe aparecer un título que sea "Tareas terminadas o eliminadas" que despliegue una lista igual a la anterior pero para tareas con estado "terminada" o "eliminada". Debe ser una sección desplegable bajo el título, o en el mismo título. Debe aparecer contraída.
A la derecha del este título pero pegado al margen derecho del listado debe haber un botón que diga "Volver" que lleve al dashboard.

## 

## Ficha "Tarea"

El título de la sección debe ser unidad\_nombre seguido por tarea\_nombre en formato título (cada palabra con mayúscula al inicio
En la parte superior de la ficha debe haber un menú desplegable para seleccionar otras "Tareas" del proyecto correspondiente al proyecto de la ficha.

La ficha debe tener 2 tarjetas sin títulos, una sobre la otra de todo el ancho disponible y ambas con fondo blanco.
La primera debe ser una tarjeta sin título con "Descripción" (tarea\_descripcion) en negrita
La segunda debe ser una tarjeta sin título con fondo blanco con la siguiente información:

* "Descripción": (tarea\_descripcion) en negrita
* "Estado de la tarea": (tarea\_estado)
* "Responsable" (tarea\_responsable)
* "Contraparte" (tarea\_contraparte)
* "Fecha inicio" (fecha\_inicio\_proy). Si no hay fecha\_inicio\_proy, se debe mostrar tarea\_fecha\_creacion.
* "Fecha término proyectada": (fecha\_fin\_proy). Cuando tarea\_estado cambia a "terminada" o "eliminada, fecha\_fin\_real toma el valor de la fecha del día del cambio. y "fecha_fin_proy" ya no se debe poder editar.
* "Fecha término real": (fecha\_fin\_real). agregar una nota que diga "Para modificar, ir a Admin"
* "Porcentaje de avance" (tarea\_pct)
* "Alerta" (con\_alerta)

El contenido de cada campo debe mostrarse como texto plano, no como campo editable, hasta que se haga click en el botón "Editar"




Botones:
Deben haber 3 botones, uno sobre el otro alineados a la izquierda:

* Botón de "Editar" de 100 px de ancho (con ícono), habilita la edición en todos los campos. "Fecha inicio" y	 "Fecha término" deben mostrar un calendario desplegable para permitir modificar. "Estado de la tarea" debe mostrar un menú desplegable con los estados disponibles.
* Botón de "Guardado" de 100 px de ancho (con ícono)
* Botón de "Eliminar" de 100 px de ancho (con ícono), debe cambiar el estado a "eliminada", y cargar la siguiente ficha siguiendo el orden de las Ids. Si es la última tarea del proyecto, debe volver a la 1ra tarea del proyecto.



"Unidad Negocios" debe ser un link que abra la ficha de la unidad
"Proyecto" debe ser un link que abra la ficha del proyecto. No mostrar proyectos que estén en estado "terminado" o "eliminado"

Bajo la ficha debe aparecer un botón que diga "Volver" que lleve al dashboard.



# Otros criterios generales:

No incorporar más información, títulos o textos que los descritos.
No utilizar ni mostrar los nombres de los campos de la base de datos, siempre usar textos descriptivos basados en estas instrucciones.
No utilizar íconos ni emojis de ningún tipo excepto donde se indique.

