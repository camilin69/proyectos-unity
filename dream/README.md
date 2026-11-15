# DREAM — escenarios en Blender y C++ / OpenGL

Trabajo independiente dentro de la rama `dream`. El visor no utiliza Unity.

## Alcance completo

El objetivo actual es reproducir los **13 escenarios distintos de los cuatro
videos**, respetando sus referencias, texturas, iluminación y movimiento.
`validation/all-scenes-plan.json` registra cada escenario, todas sus apariciones,
evidencias, pasos de construcción y estado. Los regresos a un mismo lugar se
comparan como vistas adicionales; los cierres editoriales no son otros lugares.

| Video | Escenarios |
|---|---|
| 35 | Atrio inundado, paseo de palmeras, escalera al cielo, habitación de nubes |
| 42 | Cocina a la pradera, salida al océano, pasillo ondulado, pasarela acuática |
| 51 | Árbol monumental sobre la ladera |
| 52 | Transporte de cristal, atrio acuático, ascensor acuario, sala planetaria |

Hay **6 prototipos recorribles, 7 escenarios sin versión ejecutable y 0 escenas
aceptadas como reproducción visual terminada**. La habitación, el atrio acuático,
la cocina, la escalera al cielo, el pasillo y la salida al océano tienen materiales y perfiles propios.
Los demás escenarios no se consideran implementados por estar inventariados.

La salida al océano tiene estudios editables en Blender: `blender/ocean_exit.blend`
con los materiales base y `blender/ocean_exit_water.blend` con agua animada.
La exportación recorrible para C++/OpenGL está en `blender/v42_ocean_exit.blend`.
Incluye el vestíbulo, azulejos rosas, franja crema, carteles, bordes bajos, poste,
agua interior y océano exterior. El visor anima el oleaje con un shader; no depende
de Unity ni exporta una simulación de Blender. La última comparación es
`validation/ocean-exit/runtime-comparison-v6.png` y el informe del candidato está
en `validation/ocean-exit/runtime-candidate-v6.json`. Los azulejos y la luz del
revestimiento mejoraron, pero la espuma, el color del agua interior, el poste y
algunos reflejos siguen alejados de la referencia; la escena continúa sin
aceptación visual final.

El pasillo multicolor ya tiene un prototipo editable en
`blender/wave_corridor.blend`, con diez imágenes empaquetadas y dos cámaras de
comparación. También se puede recorrer en OpenGL con `--scene wave_corridor`.
El dibujo del suelo continúa por peldaños, contrahuellas y vestíbulo.
Se revisaron una cuadrícula de UV y dos renders con materiales; las comparaciones
están en `validation/wave-material-comparison.png` y
`validation/wave-secondary-comparison.png`. Todavía difieren el fondo, los
desniveles, la base de las puertas y los reflejos. La revisión actual añade una
base continua a los bordes oscuros, dos rótulos rojos, un pulsador y dos registros
en la pared. Las capturas actuales son `validation/wave-details-v7.png` y
`validation/wave-details-v7-secondary.png`; la comparación anterior conserva su
estado histórico. La integración actual conserva los mapas y la cámara inclinada,
incluye siete luces y permite bajar y subir los doce peldaños, con colisiones
en las columnas del vestíbulo. Los reflejos de luminarias son una aproximación
por emisor; todavía faltan reflejos del entorno y sombras equivalentes a Blender.
El informe actual es `validation/wave-runtime-integration.json`; la comparación
con el video y el render actual de Blender está en
`validation/wave-runtime-comparison.png`. Los informes `wave-details-review.json`
y `wave-material-review.json` conservan las etapas anteriores a la integración.

Existe una variante editable del vestíbulo en
`blender/wave_corridor_hall_candidate.blend`: añade pilares, filas laterales de
lámparas y elementos horizontales observados al fondo. Se conserva por separado:
en las dos vistas comparadas, la base del pilar principal queda unos 60–70 píxeles
demasiado abajo. Sus dimensiones y la interpretación de las barras siguen
pendientes de un ajuste conjunto de cámaras y niveles. Esta variante no reemplaza
la exportación recorrible. Véanse `validation/wave-hall-comparison.png` y
`validation/wave-hall-review.json`; los mapas permanecen empaquetados en el `.blend`.

La revisión de movimiento está en `blender/wave_corridor_motion_candidate.blend`.
Contiene siete cámaras estimadas a partir de puntos seguidos en el video. Los
renders de 14, 15,5 y 17 segundos están comparados con sus referencias en
`validation/wave-motion/comparison.png`. En la última vista la puerta ya sale
del encuadre, pero todavía difieren la entrada al vestíbulo, las escaleras y los
bordes del suelo. Es un estudio gris separado, sin aceptación visual ni nueva
exportación OpenGL. `validation/wave-motion/review.json` registra los errores,
las comprobaciones del modelo y la conservación de las texturas originales.

La variante `blender/wave_corridor_terminal_candidate.blend` desarrolla esa
entrada: incorpora dos barandas altas, prolonga los últimos escalones más allá
de las paredes y cierra el suelo a ambos lados. Se comprobaron los cuatro apoyos
de los postes sobre la malla real y se revisó el acceso desde atrás. La comparación
de tres vistas está en `validation/wave-terminal/comparison.png`; el informe
`validation/wave-terminal/review.json` conserva también las diferencias pendientes.
El fondo del vestíbulo continúa provisional. El ajuste de la parte superior de
la abertura empeora en la vista de 17 segundos y requiere revisar la interpretación
del techo. Esta variante tampoco sustituye el prototipo OpenGL ni sus texturas.

La revisión posterior `blender/wave_corridor_aperture_candidate.blend` corrige
las referencias de esas esquinas y prueba dos finales de pared a distinta
profundidad. Sobre las mismas observaciones corregidas, el error de las esquinas
en cuatro vistas reservadas baja de 11,8 a 4,3 píxeles frente a la hipótesis de
paredes alineadas. Se revisaron cuatro renders reales y se verificó la unión
del techo; el fondo del vestíbulo sigue provisional. Véanse
`validation/wave-aperture/comparison.png` y `validation/wave-aperture/review.json`.
Las cifras anteriores del techo se conservan como historia, pero usaban otros
puntos de referencia y no son directamente comparables con este ajuste.

El estudio del vestíbulo continúa en
`blender/wave_corridor_hall_structure_candidate.blend` y su variante con materiales
`blender/wave_corridor_hall_look_candidate.blend`. Se reconstruyeron los contornos
superiores visibles de los soportes y se añadieron filas laterales de luminarias.
La variante con materiales conserva ocho mapas empaquetados, idénticos a los PNG
de origen, y una cuadrícula de prueba verifica la cobertura de sus 83 mallas.
Las tres vistas comparadas están en `validation/wave-hall-structure/comparison.png`.
Los soportes completos todavía llegan demasiado abajo respecto al video: sus
bases, el nivel del vestíbulo y la trayectoria de cámara requieren revisión
conjunta. El patrón del suelo, los reflejos y las luminarias también difieren.
El informe `validation/wave-hall-structure/review.json` registra estas limitaciones;
la variante no sustituye la exportación OpenGL ni implica aceptación visual.

`blender/wave_corridor_wall_detail_candidate.blend` añade los dos paneles de
registro de la pared izquierda, con marcos y superficies interiores separados.
Sus esquinas se ajustaron en tres vistas y se comprobaron en otras cuatro;
el error medio cuadrático de distancia en estas últimas es de unos 5 píxeles.
La comparación `validation/wave-perspective/wall-comparison.png` y su detalle
`wall-panel-detail.png` muestran que todavía difieren la inclinación superior,
el color interior y el grosor del marco. El informe
`validation/wave-perspective/review.json` también documenta dos ensayos descartados:
una interpretación de las bases que requiere un vestíbulo desproporcionado y un
patrón de pintura que ajusta las vistas de entrenamiento pero falla en otra vista.
Estos ensayos no se aplicaron al modelo ni a OpenGL. Las texturas originales
permanecen conservadas y la variante mantiene ocho mapas empaquetados.

La cocina abierta a la pradera tiene un prototipo con materiales en
`blender/kitchen_meadow.blend`, construido con `blender/build_kitchen.py` y
los parámetros de `blender/kitchen_plan.json`. Sus capturas actuales están en
`validation/kitchen-blender.png` y `validation/kitchen-opengl.png`.
Se puede atravesar la cocina hasta la pradera y regresar. El césped denso ya está
aplicado y exportado; se comparó la luz OpenGL antes y después con el mismo encuadre.
La pared y varios controles de color se aproximan más a la referencia, pero siguen
pendientes la naturalidad del césped, el cielo, los difusores y la distribución de luz.
Blender conserva diferencias de brillo y matiz en los muebles. La evaluación es
limitada y no concede aceptación visual final.
La escalera al cielo tiene materiales, césped y fibras rosas en
`blender/stair_sky.blend`, y una exportación que permite subir y bajar sus doce
peldaños. Las vistas Blender principal y lateral están en
`validation/stair-blender.png` y `validation/stair-side-blender.png`.
El césped próximo aún resulta oscuro y las hojas/fibras se ven rígidas;
también falta mejorar la luz de las huellas y la cobertura de los laterales verdes.
La revisión del marco tiene frente, retornos y reverso sólidos con pintura rosa
continua. Sus vistas están en `validation/stair-frame-*-v5.png`; el nuevo resultado
OpenGL es `validation/stair-frame-opengl-v5.png`. Se corrigió una sombra rectangular
del primer export sin cambiar la forma de la pared ni su material. Las capturas
Blender v5 preceden esa subdivisión y no se presentan como renders posteriores.
El catálogo ejecutable es `assets/scene_catalog.cat`: 6 disponibles de 13.
Los informes anteriores conservan el inventario que existía cuando se ejecutaron;
el estado actual está en `validation/all-scenes-plan.json` y `validation/status.json`.

## Estado

Hay una primera habitación pastel editable en Blender y recorrible en OpenGL:
azulejos rosa/menta, puerta abierta hacia un cielo de nubes, ventana, cortinas
de cuadros, radiador y suelo con reflejo planar e iridiscencia pintada en mapas.
La cámara de comparación usa el encuadre vertical de la referencia. La referencia principal es
`referencias/estetica/evidencias/video-35/11s.png`.

También hay un atrio azul/lima basado en `video-52/05s.png`: galerías curvas,
estanque conectado a un canal curvo, cascada, jardineras, columnas informativas,
vidrio y esferas decorativas.
El agua tiene ondas geométricas, refracción según profundidad y reflejos;
las hojas tienen movimiento suave. El suelo usa su propio plano de reflexión.

**Es un prototipo visual, no una reproducción terminada de los cuatro videos.**
Se ajustaron las proporciones de ventana, radiador y azulejos, la posición
de las nubes en ambos huecos y el suelo continuo con manchas de color localizadas.
La calibración de color de paredes, cielo y suelo está documentada antes y después;
todavía hay diferencias en reflejos, distribución de luz y respuesta de materiales.
En el atrio aún se debe refinar el acabado de vidrio,
la distribución de la vegetación y la arquitectura frente al video.
Las capturas de `validation/` muestran el resultado real, no una propuesta.

## Ejecutar en Windows

Requisitos: Windows de 64 bits, controlador gráfico con OpenGL 3.3, PowerShell
y MinGW-w64 GCC con `g++` en PATH. Se probó con GCC 13.2 y una Intel HD 630.
No hace falta instalar Blender para ejecutar el visor. No hay dependencias
de Unity, C#, Python ni Vulkan en el ejecutable.

Desde la raíz del repositorio:

```powershell
git switch dream
powershell -ExecutionPolicy Bypass -File .\dream\runtime\build.ps1 -Run
```

La primera compilación descarga GLFW 3.4 desde su release oficial y verifica
el SHA-256 del archivo. Las posteriores usan la copia local de `runtime/vendor/`.
La compilación enlaza las bibliotecas del compilador estáticamente; el binario
resultante solo importa DLL del sistema Windows. No se incluye el binario en Git.

Para iniciar una compilación existente:

```powershell
.\dream\runtime\build\dream.exe
```

Controles:

| Acción | Control |
|---|---|
| Caminar | W A S D |
| Correr | Mayúsculas izquierda |
| Capturar el ratón y mirar | Clic izquierdo, mover ratón |
| Liberar el ratón | Esc |
| Volver al encuadre inicial | R |
| Habitación pastel | 1 |
| Atrio con agua y plantas | 2 |
| Siguiente escenario disponible | Tab o Av Pág |
| Escenario anterior | Mayúsculas + Tab o Re Pág |
| Ampliar la ventana | Botón maximizar o arrastrar sus bordes |
| Salir | Cerrar la ventana |

En la habitación el recorrido está limitado al interior. La puerta abierta es geometría y tiene
colisión; el cielo es un entorno lejano, sin terreno exterior transitable.
En el atrio se recorre la planta baja; las galerías superiores son visuales.
Hay colisiones con el estanque, el canal, las columnas y las jardineras.
En la cocina se puede salir a una zona acotada de la pradera. En la escalera,
la altura de la cámara sigue los apoyos de cada peldaño y permite regresar.
El cielo tras el marco es un entorno lejano, sin destino exterior transitable.
En el pasillo multicolor se baja hasta el vestíbulo y se puede regresar;
las dos puertas laterales permanecen cerradas. El cierre detrás de la cámara
es una pared inferida para evitar ver el vacío, no un detalle observado del video.
El controlador admite apoyos rectangulares y escalones; todavía no implementa
rampas continuas, salto ni plataformas móviles.
En la salida al océano se puede recorrer el vestíbulo y avanzar por la puerta hacia
el agua. La superficie animada es un shader aproximado; la profundidad, las olas y
los reflejos todavía no igualan el video.

Para iniciar directamente en el atrio:

```powershell
.\dream\runtime\build\dream.exe --scene atrium
```

Para abrir la cocina:

```powershell
.\dream\runtime\build\dream.exe --scene kitchen_meadow
```

Para abrir la escalera al cielo:

```powershell
.\dream\runtime\build\dream.exe --scene stair_sky
```

Para abrir el pasillo multicolor:

```powershell
.\dream\runtime\build\dream.exe --scene wave_corridor
```

Para abrir la salida al océano:

```powershell
.\dream\runtime\build\dream.exe --scene v42_ocean_exit
```

`--list-scenes` enumera los 13 escenarios e indica cuáles están disponibles.
`--validate-scenes` comprueba los recursos de las escenas disponibles sin abrir una ventana.

El visor usa MSAA de 4 muestras para la geometría opaca y mantiene FXAA al
presentar la imagen. Esto mejora la continuidad de juntas y tubos pequeños.
Los reflejos siguen a media resolución; agua y vidrio se componen con una muestra
por píxel. Se puede cambiar la cobertura al iniciar con `--samples 2` o
`--samples 0`; el último conserva FXAA pero desactiva MSAA. `--samples 4`
selecciona el ajuste predeterminado. El coste depende de la resolución y la GPU.

## Archivos

- `blender/pastel_room.blend`: escena editable, con las imágenes empaquetadas.
- `blender/atrium.blend`: atrio editable con agua, vegetación y arquitectura.
- `blender/kitchen_meadow.blend`: cocina y pradera con materiales propios.
- `blender/stair_sky.blend`: escalera con apoyos, césped, fibras y marco hacia el cielo.
- `blender/wave_corridor.blend`: pasillo pastel editable en fase de ajuste, con texturas incluidas; también tiene una exportación recorrible en OpenGL.
- `blender/build_wave_corridor.py`, `blender/finish_wave_corridor.py`: construcción y aplicación de materiales del pasillo; ejecutar dentro de Blender mediante MCP.
- `blender/wave_corridor_details.py`: bordes, rótulos, pulsador y registros del pasillo; dimensiones estimadas desde las referencias.
- `blender/finish_kitchen.py`, `blender/finish_stair_sky.py`: aplicación de materiales y luz; los ajustes requieren comparación posterior.
- `blender/build_atrium.py`: construcción del atrio; admite una fase de volúmenes simples.
- `blender/build_room.py`: construcción reproducible de la habitación dentro de Blender.
- `blender/curtain_mesh.py`: cortinas cerradas con pliegues variables y UV continuos, compartidas entre ambos renderizadores.
- `blender/export_runtime.py`: exportación de geometría evaluada, materiales y oclusión local.
- `blender/make_textures.py`: texturas procedurales originales; requiere NumPy y Pillow.
- `blender/make_cloud_sky.py`: cielo con volumen precalculado, sombras lavanda y panorama sin costuras; requiere también SciPy.
- `blender/make_room_finishes.py`: mapas de color, normal y distorsión del suelo; requiere NumPy, Pillow y SciPy.
- `blender/floor_ripple.py`: campo de altura continuo y reproducible que genera las normales del suelo.
- `blender/bake_room_probe.py`: captura seis vistas del interior mediante un temporizador de Blender.
- `blender/pack_room_probe.py`: convierte esas vistas al mapa de reflexión del visor; requiere NumPy, Pillow y SciPy.
- `assets/pastel_room.glb`: intercambio estándar de geometría/materiales. No representa todos los efectos del visor.
- `assets/pastel_room.dreammesh`: malla utilizada por el visor, Z arriba, metros.
- `assets/pastel_room.json`: inventario, cámara y datos de exportación.
- `assets/atrium.*`: malla, GLB, inventario y configuración del atrio.
- `assets/kitchen_meadow.*`, `assets/stair_sky.*`, `assets/v42_ocean_exit.*`: exportaciones de los prototipos.
- `runtime/tests/ocean_exit_navigation.cpp`: comprueba que el jugador atraviese la puerta y no cruce los bordes bajos.
- `assets/scene_catalog.cat`: 13 IDs, disponibilidad y perfiles explícitos de recursos.
- `assets/*.scene`: cámara, exposición y colisiones; `*.draws`: grupos transparentes ordenados por distancia.
- `assets/textures/`: mapas compartidos; PNG para Blender y BMP para el cargador C++.
- `blender/prepare_ocean_runtime_maps.py`: convierte los PNG originales del océano a mapas RGB24 para el visor.
- `blender/prepare_ocean_exit_runtime.py`: asigna perfiles de material y navegación antes de `blender/export_runtime.py`.
- `assets/textures/room_probe.*`: panorama interior estático y metadatos de posición, límites y procedencia.
- `runtime/src/`, `runtime/shaders/`: código C++17 y GLSL 3.30.
- `referencias/estetica/`: cuatro análisis JSON, videos originales, fotogramas y recortes conservados.

Los recortes de los videos son referencias con iluminación y perspectiva ya
presentes; no son mapas PBR originales recuperados. Se conservan junto con su
procedencia. Los mapas de `assets/textures/` son una recreación procedural.
La iridiscencia tiene colores fijos y reflejos dependientes de la vista; no es
una simulación física de película delgada. Las nubes son una textura de entorno
LDR precalculada, sin volumen ni paralaje durante el recorrido.
El suelo de la habitación es una superficie cerrada continua con un único mapa
de damero y manchas (`floor_surface_albedo`), un mapa normal para Blender y
un mapa de inclinación/máscara (`floor_flow`) para OpenGL. Los mapas anteriores
`floor_pink_albedo` y `floor_mint_albedo` se conservan como variantes de referencia.
Las ondulaciones combinan escalas de 1,25 m, 38 cm y 11 cm, con amplitud
irregular en coordenadas del suelo. Normal y distorsión derivan de la misma
altura; sus canales de inclinación coinciden. No dependen de la cámara ni de
las manchas de color. El damero conserva rosa y menta sin la antigua absorción
azul que se usaba para compensar el reflejo exclusivo del cielo.

El metal de la habitación usa un mapa de reflexión interior LDR estático,
`room_probe`, con corrección de perspectiva aproximada según los límites de la
habitación y filtrado según rugosidad. No contiene objetos dinámicos ni radiancia
HDR, y no resuelve iluminación global. Debe regenerarse después de cambiar la
geometría, los materiales o las luces del interior. El suelo conserva su reflejo
planar independiente.
Un retorno de luz rectangular desde el suelo complementa el reflejo del metal;
se filtra por rugosidad y tamaño de píxel y cambia con la posición del observador.
Es una aproximación de iluminación indirecta sin oclusión dinámica. En Blender,
luces con receptores definidos equilibran pared, marcos y cromo. Estos aportes
no convierten el mapa LDR en iluminación global ni se trasladan dentro del GLB.
La revisión v7 reduce el relleno de la cerámica frontal alta con una transición
suave en coordenadas del mundo. En Blender, un retorno cálido limitado a la
puerta corrige el matiz azul sin cambiar la exposición de toda la habitación.
Las dos cortinas tienen grosor de 1,6 mm, bordes curvos y pliegues variables;
conservan su mapa de cuadros. La habitación suma 10.616 triángulos tras añadir seis conexiones del radiador.
`validation/room-radiator-v9.json` documenta ese detalle y sus capturas;
los informes y renders v7 se conservan como evidencia histórica.

## Editar y exportar desde Blender

Se creó con Blender 5.2.1. Abrir `blender/pastel_room.blend` y seleccionar la
escena `DREAM_PastelRoom`. El archivo conserva también la escena previa.

Los scripts de construcción y exportación se ejecutan **dentro de Blender**
mediante su editor de texto o Blender MCP. El constructor reemplaza únicamente
los objetos de `DREAM_PastelRoom`; no ejecutar sobre cambios manuales de esa
escena sin guardar primero otra copia.
Para el atrio se usa `DREAM_Atrium` y `build_atrium.py`, con el mismo exportador.

Para regenerar los mapas antes de reconstruir las escenas:

```powershell
python dream/blender/make_textures.py --sky regenerate
python dream/blender/make_room_finishes.py
python dream/blender/make_atrium_textures.py
```

`make_textures.py --sky reuse` conserva el cielo existente. Para crear una
alternativa separada, usar `make_cloud_sky.py --output-stem cloud_sky_candidate`.
`make_room_finishes.py` regenera por defecto los mapas activos en
`assets/textures/`. Para experimentar sin reemplazarlos, indicar otra carpeta:

```powershell
python dream/blender/make_room_finishes.py --output-dir dream/validation/floor-variant
```

Después de regenerar mapas, el flujo de la habitación es:

1. Ejecutar `build_room.py` dentro de Blender, o abrir y editar la escena existente
   `DREAM_PastelRoom` si se quieren conservar cambios manuales.
2. Ejecutar `bake_room_probe.py` dentro de Blender. Programa seis capturas de
   320×320, una cara por turno del temporizador, y devuelve el control antes de
   terminar. Consultar el estado de la escena hasta que indique `complete`;
   no lanzar otra captura mientras siga `running`:

   ```python
   import bpy, json
   print(json.loads(bpy.data.scenes['DREAM_PastelRoom']['dream_probe_bake_state']))
   ```

   Si indica `failed`, revisar el campo `error` antes de continuar. Al completar,
   las seis imágenes y `manifest.json` quedan en `validation/room-probe-faces/`.
   El script restaura la cámara y los ajustes de render originales.
3. Fuera de Blender, con NumPy, Pillow y SciPy instalados, ejecutar:

   ```powershell
   python dream/blender/pack_room_probe.py
   ```

   Produce `assets/textures/room_probe.png`, `.bmp` y `.json` a partir de las seis
   caras terminadas. El PNG y el BMP contienen el mismo panorama de 1024×512.
4. Con `DREAM_PastelRoom` activa en Blender, ejecutar `export_runtime.py` para
   guardar la escena y exportar la malla, materiales y oclusión. Reiniciar el visor
   para cargar los mapas y la geometría actualizados.

La escena fuente incluye una sonda local de reflexión y una sonda planar para
EEVEE. Los tubos del radiador tienen tapas planas y normales separadas de los
laterales; el exportador conserva las normales por esquina de la malla evaluada.
Las sondas de Blender, los reflejos, el agua y la iluminación específica del visor
no se transfieren completos mediante GLB: el visor implementa sus efectos en GLSL
y carga `room_probe.bmp` por separado. Exportar únicamente el GLB no reproduce
todo el acabado de Blender ni del visor.

El exportador produce el formato `DREAMM02`: cabecera de 8 bytes, dos enteros
uint32 (materiales/vértices), 8 float32 por material y 10 float32 por vértice
(posición, normal, UV, índice de material, oclusión). Todos los valores son
little-endian. El GLB estándar usa la conversión de ejes propia de glTF.

El visor admite hasta 32 materiales. Los tipos actuales son 0 = estándar,
1 = suelo reflectante, 2 = tejido, 3 = cerámica, 4 = agua, 5 = hojas,
6 = vidrio, 7 = señal luminosa, 8 = esfera decorativa, 9 = cascada,
11 = césped y 12 = tejido afelpado de la escalera.
El séptimo float indica opacidad y el octavo la variante de albedo del suelo.
La variante 2 identifica el suelo pastel continuo del visor actual.
El perfil del océano da a los tipos 7 y 8 sus señales y carteles propios.
Cámara, exposición, colisiones y apoyos con altura se cargan desde `.scene`.
El catálogo asigna perfiles propios: habitación 0, atrio 1, cocina 2, escalera 3,
pasillo 4 y salida al océano 5. Esta última usa una cámara con centro desplazado
verticalmente para conservar el encuadre de la puerta.
La iluminación de cada perfil y los efectos de agua/fibras siguen siendo
aproximaciones del visor; las luces de Blender no se transfieren automáticamente.
Las esferas usan un mapa procedural decorativo, no un mapa geográfico fiel.

## Verificación reproducible

```powershell
.\dream\runtime\build\dream.exe --hidden --smoke --frames 720 --width 1280 --height 720 --capture .\dream\validation\room-walk.ppm
```

La prueba crea un contexto OpenGL real, comprueba el sentido del ratón, recorre
la habitación con pasos de tiempo fijos y cambia dos veces el tamaño de ventana
para verificar el framebuffer del reflejo. Imprime `gl_error=0` al terminar bien.
La captura es PPM. Es una prueba de integración; no certifica rendimiento en
pantalla completa ni reemplaza una sesión de juego manual.

Para comprobar la navegación de la salida al océano después de compilar:

```powershell
g++ -std=c++17 -O2 -Wall -Wextra -I .\dream\runtime\src .\dream\runtime\tests\ocean_exit_navigation.cpp -o .\dream\runtime\build\ocean_exit_navigation.exe
.\dream\runtime\build\ocean_exit_navigation.exe .\dream\assets\v42_ocean_exit.scene
```

Prueba de agua, cambio de escena, redimensionado y regreso al atrio:

```powershell
.\dream\runtime\build\dream.exe --scene atrium --hidden --smoke --cycle --frames 720 --width 1280 --height 720
```

`validation/verify_assets.py atrium` valida la malla y el GLB con Python estándar.
`validation/navigation_test.cpp` comprueba las colisiones; la revisión histórica
de habitación/atrio pasó 69.000 comprobaciones con las 32 cápsulas del canal.
`validation/verify_animation.py` compara capturas a `--time 0` y `--time 2`
(requiere NumPy y Pillow); las ondas, la cascada y las hojas deben cambiar y una región
estática debe permanecer igual. El vidrio se ordena por objetos, no por píxeles:
geometría transparente entrecruzada compleja necesitará otro tratamiento.

`validation/room-comparison.png` muestra referencia, Blender y OpenGL con el mismo
aspecto vertical. `room-geometry-review.json` registra los hitos de composición;
`room-look-before-v7.json` y `room-look-after-v7.json` registran color por regiones.
Estas medias son diagnósticos, no porcentajes de fidelidad. La evaluación visual
y sus diferencias pendientes están en `fidelity-review.json`.
Para investigar materiales, `--debug-shading 1`, `2` o `3` muestra albedo,
normales u oclusión; el valor 0 conserva el render normal.
`validation/aa-validation.json` y `aa-detail-comparison.png` documentan la
comparación de cobertura sin MSAA y con 4 muestras, junto con las pruebas de
redimensionado y cambio de escena. Sus tiempos corresponden a contextos ocultos
sin sincronización vertical y al shader indicado en el informe; no garantizan
FPS en pantalla completa ni verifican por sí solos la calibración visual final.
`validation/room-render-v7.json` registra la integración posterior de materiales,
reflejos y mapas, con los hashes de la captura y sus activos. Las imágenes
`floor-finish-v4-candidate-*` documentan una variante histórica; el suelo activo
usa la versión v6 registrada en `assets/textures/floor_finish.json`.
`room-light-regions-v6.json` documenta muestras de puerta, marcos, paredes y
baldosas que guiaron esta pasada; los borradores identificados allí son pruebas
intermedias, no la captura final.
`curtain-v7-topology.json` comprueba el cierre y las UV de las cortinas;
`room-light-v7.json` y `room-floor-v7.json` documentan los ensayos de luz y
reflejo anteriores a la exportación final. Los controles funcionales y los
informes visuales identifican por separado qué demuestra cada prueba.
Los resultados y hashes v7 describen aquella versión de habitación/atrio;
no se presentan como pruebas recién ejecutadas de la versión actual del catálogo.

Para cocina, `kitchen-runtime-integration.json`, `kitchen-navigation-validation.json`
y `kitchen-look-initial.json` separan integración, recorrido y diferencias visuales.
Esos informes iniciales conservan sus resultados históricos.
`kitchen-asset-validation-v3.json` comprueba el export con césped denso;
`kitchen-look-v3.json` compara OpenGL antes/después y los renders Blender v3/v4
por separado. La captura anterior a la calibración se conserva en
`kitchen-opengl-prelight-v3.png`; el ajuste sólo modifica el perfil de cocina.
`stair-navigation-validation.json` registra 2.232 comprobaciones, 705 posiciones,
14 apoyos y una subida/bajada de 1,92 m. `stair-sky-geometry-review.json` comprueba
los activos de la escalera; `stair-profile-regression.json` registra el control
de los perfiles anteriores. `stair-look-initial.json` compara cuatro iteraciones
Blender y conserva las diferencias pendientes. Estos PASS técnicos no conceden
aceptación visual. Cada informe identifica la versión de activos que comprobó.
`stair-frame-v5.json` verifica el marco sólido, las tres vistas Blender y el export
actual de 353.922 triángulos. Su captura OpenGL pasó con `gl_error=0`; el archivo
de navegación sigue idéntico, sin atribuir una nueva prueba de recorrido.
La corrección local del marco no concede aceptación visual a la escalera completa.
`room-radiator-v9.json` registra las seis conexiones nuevas del radiador y confirma
que la geometría anterior y la cámara permanecen iguales.

## Próximas etapas

1. Refinar los seis prototipos frente a todas sus vistas de referencia: forma, luz, materiales y movimiento.
2. Construir los siete escenarios sin versión ejecutable siguiendo el inventario y los pasos de sus análisis, empezando por volúmenes y encuadre.
3. Incorporar sus recursos y perfiles al catálogo existente; ampliar navegación para rampas, terreno o plataformas cuando la referencia lo requiera.
4. Exportar y comprobar cada escenario: recorrido, patrones y UV, iluminación, reflejos, agua, vegetación y movimiento cuando aparezcan en su video.

Primero se verifica cada escena por separado. OpenGL 3.3 es la base actual;
Vulkan no está implementado. La licencia de GLFW está en `runtime/licenses/`.
