# DREAM — escenarios en Blender y C++ / OpenGL

Trabajo independiente dentro de la rama `dream`. El visor no utiliza Unity.

## Estado

Hay una primera habitación pastel editable en Blender y recorrible en OpenGL:
azulejos rosa/menta, puerta abierta hacia un cielo de nubes, ventana, cortinas
de cuadros, radiador y suelo con reflejo planar. La referencia principal es
`referencias/estetica/evidencias/video-35/11s.png`.

**Es un prototipo visual, no una reproducción terminada de los cuatro videos.**
Faltan nubes más naturales, el acabado iridiscente del suelo y una calibración
más cercana de cámara/luz/color. Agua, vegetación y atrio siguen pendientes.
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
| Ampliar la ventana | Botón maximizar o arrastrar sus bordes |
| Salir | Cerrar la ventana |

El recorrido está limitado al interior. La puerta abierta es geometría y tiene
colisión; el cielo es un entorno lejano, sin terreno exterior transitable.

## Archivos

- `blender/pastel_room.blend`: escena editable, con las imágenes empaquetadas.
- `blender/build_room.py`: construcción reproducible de la habitación dentro de Blender.
- `blender/export_runtime.py`: exportación de geometría evaluada, materiales y oclusión local.
- `blender/make_textures.py`: texturas procedurales originales; requiere NumPy y Pillow.
- `assets/pastel_room.glb`: intercambio estándar de geometría/materiales. No representa todos los efectos del visor.
- `assets/pastel_room.dreammesh`: malla utilizada por el visor, Z arriba, metros.
- `assets/pastel_room.json`: inventario, cámara y datos de exportación.
- `assets/textures/`: mapas compartidos; PNG para Blender y BMP para el cargador C++.
- `runtime/src/`, `runtime/shaders/`: código C++17 y GLSL 3.30.
- `referencias/estetica/`: cuatro análisis JSON, videos originales, fotogramas y recortes conservados.

Los recortes de los videos son referencias con iluminación y perspectiva ya
presentes; no son mapas PBR originales recuperados. Se conservan junto con su
procedencia. Los mapas de `assets/textures/` son una recreación procedural.

## Editar y exportar desde Blender

Se creó con Blender 5.2.1. Abrir `blender/pastel_room.blend` y seleccionar la
escena `DREAM_PastelRoom`. El archivo conserva también la escena previa.

Los scripts de construcción y exportación se ejecutan **dentro de Blender**
mediante su editor de texto o Blender MCP. El constructor reemplaza únicamente
los objetos de `DREAM_PastelRoom`; no ejecutar sobre cambios manuales de esa
escena sin guardar primero otra copia. Después de editar, ejecutar el exportador
con `DREAM_PastelRoom` activa y reiniciar el visor para cargar la nueva malla.

El exportador produce el formato `DREAMM02`: cabecera de 8 bytes, dos enteros
uint32 (materiales/vértices), 8 float32 por material y 10 float32 por vértice
(posición, normal, UV, índice de material, oclusión). Todos los valores son
little-endian. El GLB estándar usa la conversión de ejes propia de glTF.

El visor admite hasta 32 materiales. Los tipos actuales son 0 = estándar,
1 = suelo reflectante, 2 = tejido, 3 = cerámica. La iluminación, el límite de
recorrido y el plano de reflexión todavía están configurados para esta habitación.

## Verificación reproducible

```powershell
.\dream\runtime\build\dream.exe --hidden --smoke --frames 720 --width 1280 --height 720 --capture .\dream\validation\room-walk.ppm
```

La prueba crea un contexto OpenGL real, comprueba el sentido del ratón, recorre
la habitación con pasos de tiempo fijos y cambia dos veces el tamaño de ventana
para verificar el framebuffer del reflejo. Imprime `gl_error=0` al terminar bien.
La captura es PPM. Es una prueba de integración; no certifica rendimiento en
pantalla completa ni reemplaza una sesión de juego manual.

## Próximas etapas

1. Afinar nubes, reflejos iridiscentes, luz y encuadre frente a la referencia.
2. Incorporar agua con ondas, reflejos y profundidad aparente.
3. Vegetación con variación de silueta y movimiento moderado.
4. Construir el atrio azul/lima con arquitectura curva, agua y vidrio.

Primero se verifica cada escena por separado. OpenGL 3.3 es la base actual;
Vulkan no está implementado. La licencia de GLFW está en `runtime/licenses/`.
