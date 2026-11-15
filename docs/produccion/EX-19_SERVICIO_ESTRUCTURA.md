# EX-19 · Servicio térmico y estructura

Tres modelos originales con fuente Blender, FBX, prefab, UV y atlas PBR 1024 (BaseColor, Metallic, Roughness y Normal). Los bakes se ejecutaron individualmente a través del servidor Blender MCP en puerto 9877, conservando las escenas existentes.

| Ficha | Asset | Triángulos | Dimensiones Blender X/Y/Z |
|---|---|---:|---|
| OBJ-004 | UnidadTermica | 6136 | 1.20 / 0.67 / 1.00 m |
| OBJ-011 | NucleoSellado | 3004 | 1.00 / 0.645 / 0.81 m |
| OBJ-013 | VigaDeformada | 2121 | 4.025 / 0.327 / 0.95 m |

Las conexiones y asas explican los pequeños salientes sobre las dimensiones nominales. La unidad térmica tiene radiador con 21 aletas de espesor real, colectores, compresor con aisladores y apoyos, tuberías internas, cubierta de servicio y acoples traseros. El núcleo tiene carcasa, tapa atornillada, junta, terminales protegidos, precinto de cable y patas aislantes. La viga tiene perfil en I de 32 cm de altura, alas de 22 mm y alma de 18 mm, pliegue localizado, extremo irregular y placas de unión con pernos.

La primera exportación de la viga no superó la comparación de topología: Unity descartaba triángulos degenerados del bisel y de las tapas. Se trianguló y limpió la fuente, conservando el UV, y se volvió a hornear Normal. El import final coincide en 2121 triángulos y pasa la comparación de muestras de vértices. La receta incluye esa limpieza para futuras reconstrucciones.

## Integración y evidencia

M014 en REG-S1/P02 sustituye la caja de viga por OBJ-013, a escala real y con origen (7,-18,13). FurniturePlacement.TryPlace mantiene esta sustitución al regenerar la región. La colisión usa ocho cajas por tramos y SurfaceTag metálico. No se desplazó PICK-W01 ni se modificó su cantidad o identidad.

Unidad térmica y núcleo son prefabs preparados, sin colocación regional todavía. Faltan sus conexiones externas, montaje junto al sistema criogénico y audio localizado. La viga requiere el conjunto de derrumbe de OBJ-012 para terminar la relación narrativa con la estructura dañada. La captura de sala muestra explícitamente los placeholders restantes; no se declara final el entorno.

61/61 Edit Mode, 1.58 s, job 0cff3e98d4434aec920e6a3860a18637. Los tres casos añadidos comprueban dimensiones, origen en suelo, material con mapas y colisión. FurnitureReview compara topología y ejes con las fuentes. Evidencias: SourceArt/_evidence/EX-19, con geometry.json, source_coordinates.json, axis_conversion.json, unity_import.json, bake.json, previews y edit-mode-tests.json. El diagnóstico global de albedo revisa 42 atlas sin detectar el fallo de metal negro; no equivale a aceptación artística.

No se generó una nueva build en esta entrega; la última build EX-18 es anterior a estos assets. Pendientes comunes: desgaste localizado, etiquetas legibles y revisión con iluminación final. Estado: OBJ-004/011 Prefab validado; OBJ-013 Integrado. acceptance_proven=false para las tres fichas. El objetivo de todas las 101 entradas continúa activo.
