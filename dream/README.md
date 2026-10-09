# DREAM — escenarios en Blender y C++ / OpenGL

Trabajo independiente dentro de la rama `dream`. El visor no utiliza Unity.

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
| Ampliar la ventana | Botón maximizar o arrastrar sus bordes |
| Salir | Cerrar la ventana |

El recorrido está limitado al interior. La puerta abierta es geometría y tiene
colisión; el cielo es un entorno lejano, sin terreno exterior transitable.
En el atrio se recorre la planta baja; las galerías superiores son visuales.
Hay colisiones con el estanque, el canal, las columnas y las jardineras.

Para iniciar directamente en el atrio:

```powershell
.\dream\runtime\build\dream.exe --scene atrium
```

El visor usa MSAA de 4 muestras para la geometría opaca y mantiene FXAA al
presentar la imagen. Esto mejora la continuidad de juntas y tubos pequeños.
Los reflejos siguen a media resolución; agua y vidrio se componen con una muestra
por píxel. Se puede cambiar la cobertura al iniciar con `--samples 2` o
`--samples 0`; el último conserva FXAA pero desactiva MSAA. `--samples 4`
selecciona el ajuste predeterminado. El coste depende de la resolución y la GPU.

## Archivos

- `blender/pastel_room.blend`: escena editable, con las imágenes empaquetadas.
- `blender/atrium.blend`: atrio editable con agua, vegetación y arquitectura.
- `blender/build_atrium.py`: construcción del atrio; admite una fase de volúmenes simples.
- `blender/build_room.py`: construcción reproducible de la habitación dentro de Blender.
- `blender/export_runtime.py`: exportación de geometría evaluada, materiales y oclusión local.
- `blender/make_textures.py`: texturas procedurales originales; requiere NumPy y Pillow.
- `blender/make_cloud_sky.py`: cielo con volumen precalculado, sombras lavanda y panorama sin costuras; requiere también SciPy.
- `blender/make_room_finishes.py`: mapas de color, normal y distorsión del suelo; requiere NumPy, Pillow y SciPy.
- `blender/bake_room_probe.py`: captura seis vistas del interior mediante un temporizador de Blender.
- `blender/pack_room_probe.py`: convierte esas vistas al mapa de reflexión del visor; requiere NumPy, Pillow y SciPy.
- `assets/pastel_room.glb`: intercambio estándar de geometría/materiales. No representa todos los efectos del visor.
- `assets/pastel_room.dreammesh`: malla utilizada por el visor, Z arriba, metros.
- `assets/pastel_room.json`: inventario, cámara y datos de exportación.
- `assets/atrium.*`: malla, GLB, inventario y configuración del atrio.
- `assets/*.scene`: cámara, exposición y colisiones; `*.draws`: grupos transparentes ordenados por distancia.
- `assets/textures/`: mapas compartidos; PNG para Blender y BMP para el cargador C++.
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

El metal de la habitación usa un mapa de reflexión interior LDR estático,
`room_probe`, con corrección de perspectiva aproximada según los límites de la
habitación y filtrado según rugosidad. No contiene objetos dinámicos ni radiancia
HDR, y no resuelve iluminación global. Debe regenerarse después de cambiar la
geometría, los materiales o las luces del interior. El suelo conserva su reflejo
planar independiente.

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
6 = vidrio, 7 = señal luminosa, 8 = esfera decorativa, 9 = cascada.
El séptimo float indica opacidad y el octavo la variante de albedo del suelo.
La variante 2 identifica el suelo pastel continuo del visor actual.
Cámara, exposición y colisiones se cargan desde
`.scene`; el perfil de luz y el suelo del atrio todavía tienen parámetros específicos.
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

Prueba de agua, cambio de escena, redimensionado y regreso al atrio:

```powershell
.\dream\runtime\build\dream.exe --scene atrium --hidden --smoke --cycle --frames 720 --width 1280 --height 720
```

`validation/verify_assets.py atrium` valida la malla y el GLB con Python estándar.
`validation/navigation_test.cpp` comprueba las colisiones; el export actual
pasó 69.000 comprobaciones con las 32 cápsulas del canal.
`validation/verify_animation.py` compara capturas a `--time 0` y `--time 2`
(requiere NumPy y Pillow); las ondas, la cascada y las hojas deben cambiar y una región
estática debe permanecer igual. El vidrio se ordena por objetos, no por píxeles:
geometría transparente entrecruzada compleja necesitará otro tratamiento.

`validation/room-comparison.png` muestra referencia, Blender y OpenGL con el mismo
aspecto vertical. `room-geometry-review.json` registra los hitos de composición;
`room-look-before-v5.json` y `room-look-after-v5.json` registran color por regiones.
Estas medias son diagnósticos, no porcentajes de fidelidad. La evaluación visual
y sus diferencias pendientes están en `fidelity-review.json`.
Para investigar materiales, `--debug-shading 1`, `2` o `3` muestra albedo,
normales u oclusión; el valor 0 conserva el render normal.
`validation/aa-validation.json` y `aa-detail-comparison.png` documentan la
comparación de cobertura sin MSAA y con 4 muestras, junto con las pruebas de
redimensionado y cambio de escena. Sus tiempos corresponden a contextos ocultos
sin sincronización vertical y al shader indicado en el informe; no garantizan
FPS en pantalla completa ni verifican por sí solos la calibración visual final.
`validation/room-render-v5.json` registra la integración posterior de materiales,
reflejos y mapas, con los hashes de la captura y sus activos. Las imágenes
`floor-finish-v4-candidate-*` documentan una variante histórica; el suelo activo
usa la versión v5 suavizada registrada en `assets/textures/floor_finish.json`.

## Próximas etapas

1. Afinar suavidad de reflejos, respuesta del metal y luz frente a la referencia.
2. Afinar el agua y el vidrio del atrio frente a la referencia.
3. Ajustar distribución y densidad de la vegetación, que ya tiene hojas anchas, helechos y lianas.
4. Revisar encuadres y acabado del atrio, ya construido y recorrible en planta baja.

Primero se verifica cada escena por separado. OpenGL 3.3 es la base actual;
Vulkan no está implementado. La licencia de GLFW está en `runtime/licenses/`.
