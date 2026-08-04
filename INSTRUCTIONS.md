# Nombre: "Gestión de Proyectos Casinos de Chile"

# Requerimiento

Preparar una app tipo HTML para usar con cualquier buscador para monitorear el avance en los distintos proyectos del área de proyectos de la empresa Casinos de Chile SpA.

# Definiciones generales

## Persistencia de datos, uso multiusuario y despliegue

La app será publicada y usada principalmente desde **Streamlit Cloud**, conectada al repositorio GitHub:

`https://github.com/fdo57/consola-enjoy`

El flujo correcto de desarrollo y publicación es:

**Antigravity / entorno local → commit → push a GitHub → redeploy en Streamlit Cloud**

Los cambios hechos en archivos locales o en Google Drive no llegan automáticamente a la app publicada si no son subidos al repositorio GitHub conectado a Streamlit.

### Base de datos central

La app debe contar con una **base de datos central única y compartida**, actualmente definida como Google Sheets:

`BD Consola Enjoy - central`

ID:

`1dpA2Nnk9dZ_NVkhJD1HHRBN4CH6Ry8bzm2Iuf_oXV8Y`

Reglas obligatorias:

* `localStorage` no debe ser la fuente principal de datos.
* `localStorage` sólo puede usarse como caché temporal del navegador.
* Al iniciar o refrescar la app, siempre debe cargar información desde la base central.
* Al crear, editar, terminar o eliminar una tarea o proyecto, el cambio debe guardarse inmediatamente en Google Sheets.
* Los cambios hechos por un usuario deben quedar disponibles para otros usuarios al abrir o refrescar la app.
* `data.js` puede usarse únicamente como semilla inicial si la base central está vacía.
* `data.js` no debe considerarse base viva de trabajo.
* `carga_masiva.xlsx` debe usarse sólo como plantilla o mecanismo de importación manual.
* La descarga/exportación de base de datos debe exportar la información vigente desde Google Sheets.

### Credenciales y secrets

La conexión a Google Sheets debe hacerse desde Streamlit mediante `st.secrets`.

Importante:

* El archivo `.streamlit/secrets.toml` local sirve sólo para desarrollo local.
* El archivo `secrets.toml` no debe subirse a GitHub.
* En producción, los secrets deben configurarse directamente en **Streamlit Cloud → App settings → Secrets**.
* La service account usada por Streamlit debe tener permiso de **Editor** sobre la Google Sheet central.

### Arranque correcto de la app

La app no debe abrirse directamente como `index.html` para uso real, porque en ese modo:

* no corre Streamlit,
* no se ejecuta `app.py`,
* no se ejecuta `db_manager.py`,
* no se lee `st.secrets`,
* no se conecta a Google Sheets,
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
* Todas las fechas que se muestren o en los campos a rellenar deben ser en formato DD/MM/AAAA


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

fecha\_legacy: Corresponde a fechas legacy de las minutas en word utilizadas hasta implementación de la app, que serán traspasadas desde  un archivo de carga masiva. Son sólo fechas referenciales que pueden representar fechas de inicio, fechas de fin real o fechas de fin programadas.

con\_alerta: La tarea debe ser considerada prioritaria y requiere atención especial

tarea\_fecha\_creacion: Se establece al momento de crear una tarea.

fecha\_inicio\_proy: Corresponde a la fecha de inicio proyectada de una tarea.

fecha\_inicio\_real: Corresponde a la fecha de inicio real de una tarea.

fecha\_fin\_proy: Corresponde a la fecha de fin proyectada de una tarea.

fecha\_fin\_real: Corresponde a la fecha de fin real de una tarea. Si al momento de cambiar de estado de "en desarrollo" a "terminada" o a "eliminada" no tiene valor, se debe establecer la fecha del momento del cambio.

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

* `tarea_estado` es `"en desarrollo"` o `"detenida"`.
* `tarea_fecha_creacion` tiene valor.
* `tarea_fecha_creacion` pertenece a la misma semana de la **Fecha de Informe**.

No deben usarse `fecha_legacy`, `fecha_inicio_proy` ni `fecha_inicio_real` para determinar si una tarea fue creada en la semana. La variable oficial para esta subsección es `tarea_fecha_creacion`.

#### Tareas Terminadas

Una tarea debe aparecer en **Tareas Terminadas** sólo si cumple todos estos criterios:

* `tarea_estado` es `"terminada"` o `"eliminada"`.
* `fecha_fin_real` tiene valor.
* `fecha_fin_real` pertenece a la misma semana de la **Fecha de Informe**.

La variable oficial para determinar cierre semanal es `fecha_fin_real`.

#### Actualizar Fechas

Agregar una tercera subsección dentro de **Avance Semanal** llamada **Actualizar Fechas**.

Esta subsección debe mostrar tareas que tengan inconsistencias o fechas incompletas que puedan afectar la lectura del avance semanal.

Deben aparecer en **Actualizar Fechas** las tareas que cumplan cualquiera de estos criterios:

* Tareas con `tarea_estado` `"terminada"` o `"eliminada"` y sin valor en `fecha_fin_real` o sin valor en `fecha_fin_proy`.
* Tareas sin valor en `fecha_inicio_proy` o sin valor en `fecha_inicio_real`.
* Tareas con `tarea_fecha_creacion` dentro de la misma semana de la **Fecha de Informe** y sin valor en `fecha_inicio_proy` o sin valor en `fecha_inicio_real`.

La subsección **Actualizar Fechas** es una alerta de calidad de datos. Su objetivo es indicar qué tareas requieren completar o corregir fechas antes de interpretar el avance semanal.

#### Semáforo en Avance Semanal

A la derecha del nombre de la tarea, agregar una columna con ícono de semáforo con los mismos parámetros que en **Tareas en Curso**:

* Color verde: tareas con `tarea_estado` `"en desarrollo"` y `con_alerta` en `"no"`.
* Color amarillo: tareas con `tarea_estado` `"detenida"` y `con_alerta` en `"no"`.
* Color rojo: tareas con `tarea_estado` `"en desarrollo"`, `"detenida"` o `"por iniciar"` que tengan `con_alerta` en `"si"`.

## 2\. Fecha de Informe

Fecha de generación de información en Dashboard. Por definición viene en el día en curso, con un calendario desplegable en el mismo panel lateral para consultar otras fechas. Afecta zona "Avance Semanal". Al hacer click en cualquier botón del panel lateral, "Fecha de informe" debe cambiar al día en curso.



## 3\. Proyectos

Una tabla que contiene todos los proyectos que tengan estado\_proyecto "por iniciar", "en desarrollo", "en construcción", "detenido" y las tareas que tengan estado\_tarea  "por iniciar", "en desarrollo", "detenida" ordenados de la siguiente manera, con los respectivos campos entre paréntesis:



Columna 1: UN Negocios (unidad\_nombre)
Columna 2: Proyecto (proyecto\_nombre)
Columna 3: Nombre tarea (tarea\_nombre)
Columna 4: Descripción tarea (tarea\_descripcion), los textos en esta columna no deben tener más de 4 líneas.
Columna 5: Responsable (tarea\_responsable)
Columna 6: Estado (tarea\_estado), debe ser editable
Columna 7: Avance % (tarea\_pct), debe ser editable
Columna 8: Fecha base (fecha\_legacy), debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 9: Fecha inicio (proy) (fecha\_inicio\_proy),  debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 10: Fecha fin (proy) (fecha\_fin\_proy),  debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 11: En Alerta (selector "si/no" para definir con\_alerta)
Columna 12: Terminar (botón de check)
Columna 13: Borrar (botón de borrado, cambia el estado a "eliminada", con ícono)



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

\- con\_alerta

* fecha\_inicio\_proy
* fecha\_inicio\_real
* fecha\_fin\_proy
* fecha\_fin\_real



Campos que se llenan automáticamente:

\- tarea\_id se crea automáticamente con las reglas establecidas antes

\- tarea\_estado se crea automáticamente en "en desarrollo"

\- fecha\_inicio\_proy se crea automáticamente con la fecha del día de la creación de la tarea

\- fecha\_inicio\_real se crea automáticamente con la fecha del día de la creación de la tarea

\- fecha\_legacy se crea automáticamente con la fecha del día de la creación de la tarea

\- tarea\_pct se crea automáticamente en 0

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

Columna 7: Fecha base (fecha\_legacy), debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 8: Fecha inicio (proy) (fecha\_inicio\_proy), debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 9: Fecha fin (proy) (fecha\_fin\_proy), debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.

Columna 10: En Alerta (selector "si/no" para definir con\_alerta)
Columna 11: Terminar (botón de check)
Columna 12: Borrar (botón de borrado, cambia el estado a "eliminada", con ícono)

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
Columna 7: Fecha base (fecha\_legacy), debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 8: Fecha inicio (proy) (fecha\_inicio\_proy), debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.
Columna 9: Fecha fin (proy) (fecha\_fin\_proy), debe ir el texto en negrita y al lado un botón con un calendario desplegable que permita modificarlo.

Columna 10: En Alerta (selector "si/no" para definir con\_alerta)
Columna 11: Terminar (botón de check)
Columna 12: Borrar (botón de borrado, cambia el estado a "eliminada", con ícono)



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

\- "Descripción" (tarea\_descripcion) en negrita

* "Estado de la tarea": (tarea\_estado)
* "Responsable" (tarea\_responsable)
* "Contraparte" (tarea\_contraparte)
* "Fecha según Minuta" (fecha\_legacy)
* "Fecha inicio" (fecha\_inicio\_proy). Si no hay fecha\_inicio\_proy, se debe mostrar tarea\_fecha\_creacion. Cuando tarea\_estado cambia a "en desarrollo", fecha\_inicio\_real toma el valor de la fecha del día del cambio.
* "Fecha término": (Fecha\_fin\_proy). Cuando tarea\_estado cambia a "terminada" o "eliminada, fecha\_fin\_real toma el valor de la fecha del día del cambio.
* "Porcentaje de avance" (tarea\_pct)

\- "Alerta" (con\_alerta)



El contenido de cada campo debe mostrarse como texto plano, no como campo editable, hasta que se haga click en el botón "Editar"



Botones:
Deben haber 3 botones, uno sobre el otro alineados a la izquierda:

* Botón de "Editar" de 100 px de ancho (con ícono), habilita la edición en todos los campos. "Fecha según Minuta", "Fecha inicio", "Fecha término" deben mostrar un calendario desplegable para permitir modificar. "Estado de la tarea" debe mostrar un menú desplegable con los estados disponibles.
* Botón de "Guardado" de 100 px de ancho (con ícono)
* Botón de "Eliminar" de 100 px de ancho (con ícono), debe cambiar el estado a "eliminada", y cargar la siguiente ficha siguiendo el orden de las Ids. Si es la última tarea del proyecto, debe volver a la 1ra tarea del proyecto.



"Unidad Negocios" debe ser un link que abra la ficha de la unidad
"Proyecto" debe ser un link que abra la ficha del proyecto. No mostrar proyectos que estén en estado "terminado" o "eliminado"

Bajo la ficha debe aparecer un botón que diga "Volver" que lleve al dashboard.



# Otros criterios generales:

No incorporar más información, títulos o textos que los descritos.
No utilizar ni mostrar los nombres de los campos de la base de datos, siempre usar textos descriptivos basados en estas instrucciones.
No utilizar íconos ni emojis de ningún tipo excepto donde se indique.

