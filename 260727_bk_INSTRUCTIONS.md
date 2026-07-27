# Nombre: "Gestión de Proyectos Casinos de Chile"

# Requerimiento

Preparar una app tipo HTML para usar con cualquier buscador para monitorear el avance en los distintos proyectos del área de proyectos de la empresa Casinos de Chile SpA.

# Definiciones generales

## Empresa

Casinos de Chile es una empresa que administra Casinos y Hoteles de la cadena Enjoy que cuenta con 5 complejos turísticos, llamados internamente "Unidades de Negocios" o "Unidades.

## Unidades

Los complejos turísticos o Unidades son:
- Rinconada
- Pucón
- Viña
- Coquimbo
- Chiloé
- Transversales

Las respectivas abreviaciones son:
- RI
- PU
- VI
- CQ
- CH
- TR

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

fecha\_inicio\_proy: Corresponde a la fecha de inicio proyectada de una tarea.

fecha\_inicio\_real: Corresponde a la fecha de inicio real de una tarea.

fecha\_fin\_proy: Corresponde a la fecha de fin proyectada de una tarea.

fecha\_fin\_real: Corresponde a la fecha de fin real de una tarea.

## Usuarios

Los usuarios y sus características serán 3:
- CEO de Casinos de Chile SpA.:  Necesitará lograr una comprensión general pero precisa del avance en las tareas de los distintos proyectos de forma ágil. Dispone de poco tiempo para revisar y la simpleza será clave. Consultará sólo un dashboard.
- Subgerenta de Proyectos: No tiene experiencia con medios digitales, necesitará una app limpia y fácil de usar. Esto se traduce en que cada sección que este profesional consulte debe tener el mínimo de información. Además de visualizar las mismas secciones que el CEO, deberá poder crear y editar los proyectos en la misma consola.
- Jefe de Proyectos: Será el encargado de administrar la aplicación, haciendo el troubleshooting, cargando información y haciendo mejoras que vayan siendo necesarias.

La descripción de los usuarios busca detallar la experiencia que tienen para acotar la complejidad de las distintas secciones de la app.

## Colores

Los colores a utilizar para títulos, fondos de tarjetas y otros serán:
#C04F15 para títulos
#595959 Para subtítulos, listas y otros textos
#F6C6AD Para fondos
#F2F2F2 Para fondos

# Secciones

La app tendrá 3 secciones con sus respectivos botones en el panel lateral

1. Dashboard
2. Proyectos
3. Admin



El panel lateral no debe tener ningún título



## 1\. Dashboard

En la parte superior tendrá un título que será "Proyectos En Desarrollo" y al lado tendrá un menú desplegable para filtrar por unidad de negocio.

El cuerpo del Dashboard estará separado en 3 zonas del mismo ancho, cada zona con su título que serán los siguientes:
- "Unidad de Negocio"
- "Tareas en Curso
- "Alertas"



### Zona "Proyectos por Unidad de Negocio" en dashboard

Un listado de las unidades de negocio con proyectos activos. No debe incluir proyectos con estado "terminado" o "eliminado"
A la izquierda de cada elemento debe haber un botón un número que representa la cantidad de proyectos en curso para la unidad. El botón debe ser de color gris con el texto color blanco.
Bajo cada elemento debe ir un listado con los proyectos en curso. Al hacerle click a cada elemento de la lista genera el listado de tareas en la siguiente zona "Tareas en Curso"

### Zona "Tareas en Curso"

Un listado dinámico que se genera al hacer click a un proyecto de la zona "Proyectos por Unidad" mostrando una columna con el nombre de las tareas en curso del proyecto seleccionado con estado "por iniciar", "en desarrollo" o "detenida". No mostrar tareas en estado "terminada" o "eliminada". Cada ítem de la lista corresponde al nombre de la tarea del proyecto seleccionado en la zona "Proyectos por Unidad de Negocio". Cada ítem de la lista debe ser un vínculo a la ficha de la tarea. Junto a la columna de nombre de la tarea debe haber una columna con el responsable. Al abrir la app mostrar las tareas del primer proyecto de la primera unidad de la lista de "Proyectos por Unidad" 

### Zona "Alertas"

Un listado de las tareas en curso con el campo con\_alerta en "si" en la base de datos con estado "por iniciar", "en desarrollo" o "detenida". No mostrar tareas en estado "terminada" o "eliminada". Dentro de la zona, en una columna va el unidad\_nombre correspondiente y una columna con el nombre de la tarea. Cada ítem de la lista debe ser un vínculo a la ficha de la tarea.

## 2\. Proyectos

Una tabla que contiene todos los proyectos que tengan estado\_proyecto "por iniciar", "en desarrollo", "en construcción", "detenido" y las tareas que tengan estado\_tarea  "por iniciar", "en desarrollo", "detenida" ordenados de la siguiente manera, con los respectivos campos entre paréntesis:



Columna 1: UN Negocios (unidad\_nombre)
Columna 2: Proyecto (proyecto\_nombre)
Columna 3: Nombre tarea (tarea\_nombre)
Columna 4: Descripción tarea (tarea\_descripcion), los textos en esta columna no deben tener más de 4 líneas.
Columna 5: Responsable (tarea\_responsable)
Columna 6: Estado (tarea\_estado)
Columna 7: Avance % (tarea\_pct)
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

Formulario de creación de "Nueva tarea"

Una tarjeta con los siguientes campos para llenar:
- unidad\_nombre: muestra un menú desplegable con las unidades
- proyecto\_nombre: muestra un menú desplegable con los proyectos en curso para "unidad\_nombre", con una opción "nuevo proyecto" que lleva al formulario de creacion de nuevo proyecto.
- tarea\_nombre
- tarea\_descripcion
- tarea\_responsable
- tarea\_contraparte

\- con\_alerta
- fecha\_inicio\_proy
- fecha\_inicio\_real
- fecha\_fin\_proy
- fecha\_fin\_real



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
- unidad\_nombre: muestra un menú desplegable con las unidades

\- proyecto\_nombre

\- proyecto\_descripcion



Campos que se llenan automáticamente:

proyecto\_estado se crea automáticamente como "en desarrollo"
Al final, botón "Guardar" y "Descartar", uno al lado del otro.




## 3\. Admin

En esta sección se hará la administración de la app. Contará con las siguientes sub-secciones, las que se ordenarán a modo de lista con los respectivos títulos:

"Archivo de Carga Masiva"

junto al título debe tener un botón con un ícono que represente "download" que descarga un archivo en formato .xlsx llamado "carga\_masiva.xlsx". Debe mostrar una descripción que diga "descargue la plantilla para carga de datos".



El archivo .xlsx debe tener los siguientes encabezados:

&#x09;- proyecto\_id
	- unidad\_nombre
	- proyecto\_nombre
	- proyecto\_estado
	- tarea\_id
	- tarea\_nombre
	- tarea\_descripcion
	- tarea\_responsable 
	- tarea\_estado
	- tarea\_contraparte

&#x09;- tarea\_pct
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
- Unidad: (unidad\_nombre)
- Proyectos en curso: (suma de proyectos que estén en estado "por iniciar", "en desarrollo", "en construcción" o "detenido")
- Tareas en curso: (suma de tareas que estén en estado "por iniciar", "en desarrollo", o "detenida", suma sólo las tareas de la unidad)
- Tareas en alerta: (listado de tareas con\_alerta en "si")

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

En la parte superior de la ficha debe haber un menú desplegable para seleccionar otros "Proyectos" de la Unidad correspondiente al proyecto de la ficha.

La ficha debe tener una tarjeta con fondo blanco con la siguiente información en texto grande:
- "Unidad de Negocio": (unidad\_nombre), debe ser un vínculo que lleve a la ficha de la unidad.
- "Proyecto": (proyecto\_nombre), debe mostrar sólo proyectos asociados a la unidad. debe ser editable
- "Estado del Proyecto": (proyecto\_estado), debe tener un menú desplegable con las opciones, que permita modificar el estado.
- "Tareas en curso": (cantidad de tareas, no mostrar tareas que estén en estado "terminada" o "eliminada". Cuenta sólo las tareas del proyecto)
- "Tareas en alerta": (listado de tareas con\_alerta en "si", cuenta sólo las tareas del proyecto)



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
- "Estado de la tarea": (tarea\_estado)
- "Responsable" (tarea\_responsable)
- "Contraparte" (tarea\_contraparte)
- "Fecha según Minuta" (fecha\_legacy)
- "Fecha inicio" (fecha\_inicio\_proy)
- "Fecha término": (Fecha\_fin\_proy)
- "Porcentaje de avance" (tarea\_pct)



El contenido de cada campo debe mostrarse como texto plano, no como campo editable, hazta que se haga click en el botón "Editar"



Botones:
Deben haber 3 botones, uno sobre el otro alineados a la izquierda:
- Botón de "Editar" de 100 px de ancho (con ícono), habilita la edición en todos los campos. "Fecha según Minuta", "Fecha inicio", "Fecha término" deben mostrar un calendario desplegable para permitir modificar. "Estado de la tarea" debe mostrar un menú desplegable con los estados disponibles.
- Botón de "Guardado" de 100 px de ancho (con ícono)
- Botón de "Eliminar" de 100 px de ancho (con ícono), debe cambiar el estado a "eliminada", y cargar la siguiente ficha siguiendo el orden de las Ids. Si es la última tarea del proyecto, debe volver a la 1ra tarea del proyecto.



"Unidad Negocios" debe ser un link que abra la ficha de la unidad
"Proyecto" debe ser un link que abra la ficha del proyecto. No mostrar proyectos que estén en estado "terminado" o "eliminado"

Bajo la ficha debe aparecer un botón que diga "Volver" que lleve al dashboard.



# Otros criterios generales:

No incorporar más información, títulos o textos que los descritos.
No utilizar ni mostrar los nombres de los campos de la base de datos, siempre usar textos descriptivos basados en estas instrucciones.
No utilizar íconos ni emojis de ningún tipo excepto donde se indique.



# Para siguiente versión:

En sección "Proyectos por Unidad de Negocio", al lado de cada proyecto se debe agregar un ícono de exclamación para los proyectos que tengan tareas en alerta.

En sección "Tareas en Curso" se agregará indicador tipo semáforo indicando estado de la tarea (por diseñar)

En sección "Alertas" se hará modificación para convertirla en sección con avance semanal. Va a requerir definición de fechas de creación y de cambio de estado.

En modalidad de edición de tareas no se puede cambiar el nombre. Corregir.

