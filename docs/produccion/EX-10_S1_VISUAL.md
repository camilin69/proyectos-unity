# EX-10 · Primera iteración visual de preservación S1

## Alcance

La cámara inicial, preparación y galería de preservación de P01 reciben una biblioteca modular original creada mediante Blender MCP e integrada mediante Unity MCP. Esta iteración mejora la construcción visible de las salas; no cierra el arte Tier A de brazos, armas o robots.

## Entregables

- `SourceArt/Blender/S1_ServiceKit.blend`: fuente independiente; cinco piezas con UV, escala métrica y materiales separados.
- `SourceArt/Scripts/build_s1_service_kit.py`: fabricación reproducible; conserva la escena de brazos abierta y solo reemplaza su propia escena EX10.
- `Assets/_Game/Art/Models/S1_ServiceKit.fbx`: panel sanitario con rejilla y fijaciones, tuberías con bridas, luminaria, manifold con manómetros y depósito de refrigerante.
- `Assets/_Game/Scripts/Editor/Art/S1VisualPass.cs`: integración repetible en REG-S1, suelo con UV por metros, materiales URP, señalética, luz fría de servicio y acento cálido en salida.
- `Assets/_Game/Art/S1/WorldSign.shader`: texto del mundo con prueba de profundidad para ocultarlo tras paredes.
- La regeneración de regiones invoca esta pasada para conservar el acabado nuevo.
- `PerfProbe` activa `Application.runInBackground` exclusivamente con `-autotest`, para que la medición avance al perder foco sin recurrir a `-batchmode`.

| Pieza | Triángulos de fuente | Dimensiones Blender (X/Y/Z, metros) |
|---|---:|---|
| Panel sanitario | 1 580 | 1.98 / 0.215 / 2.80 |
| Pareja de tuberías | 1 088 | 0.57 / 0.29 / 3.00 |
| Luminaria | 540 | 1.70 / 0.34 / 0.235 |
| Manifold | 784 | 0.80 / 0.423 / 1.825 |
| Depósito | 1 128 | 1.40 / 1.40 / 2.842 |

Total de biblioteca: 5 120 triángulos; el coste de escena depende de las instancias. El panel es repetido y comparte mesh/materiales. Las piezas visuales estáticas llevan BatchingStatic. No se han creado variantes LOD en esta iteración.

## Decisiones y límites

- Se conserva la geometría funcional de la escena: puertas, GUID, pickups, rutas y NavMesh. El depósito usa la cobertura/collider existente M003.
- Los accesorios de servicio son decorativos; no incorporan nuevas interacciones ni física.
- La criocámara conserva fuente, rig y clips. Su tapa recibe materiales separados de vidrio y escarcha transparentes en Unity; esto no constituye una refabricación Tier A.
- Las caras interiores de paneles y la escala FBX se revisaron en motor. Los rótulos se redujeron y se retiró el texto flotante sobre la criocámara.
- Los cinco archivos previamente modificados por el usuario se conservan. Una nueva build contendrá esos cambios locales; su commit base no equivale a un árbol limpio.
- Falta la siguiente pasada de anatomía de manos/robots, desgaste localizado, high/low donde aporte valor, animación artística y LOD. Esta escena es una mejora inicial comprobable, no aceptación visual final.

## Evidencia

- `SourceArt/_evidence/EX-10/kit_report.json`: geometría y UV medidas en Blender.
- `SourceArt/_evidence/EX-10/S1_before.png` y `S1_final.png`: misma cámara, posición y FOV en Unity; `S1_after.png` es una captura intermedia.
- `SourceArt/_evidence/EX-10/S1_door.png`: lectura de salida y paneles.
- `SourceArt/_evidence/EX-10/S1_gallery_final.png`: repetición modular y criocámaras.

Las capturas son renders del Editor Unity; por sí solas no certifican FPS ni una partida manual completa.

## Validación

- Compilación inicial sin errores C#.
- Selección de narrativa, sectores y recorrido de campaña: 8/8 aprobadas (job `39acdab54e6546ec8a339fb48d6c06ec`).
- Suite completa Play Mode: 35/35 aprobadas, 0 fallos, 166.58 s (job `2f1d6b86c44242689e855c793a2c4a9d`).
- Suite completa Edit Mode: 25/25 aprobadas, 0 fallos, 0.84 s (job `e37782f8de4040db8e89d0c2e23f2638`).
- Build Windows Release `EX10-S1`: Succeeded, 168 MB, 0 errores, 56 advertencias, 58.62 s en la compilación final. Informe: `docs/produccion/evidencia/build_EX10-S1.json`. El log contiene advertencias CS0618 por APIs obsoletas; no se ha hecho una migración general de APIs en esta tarea.
- Las 60 pruebas preceden al ajuste final de `PerfProbe`; este ajuste se comprueba mediante la ejecución real de la build. El modo de juego normal conserva su comportamiento.
- Unity añadió la referencia de InputSystem_Actions a `preloadedAssets` al construir. Los recursos temporales de pruebas fueron retirados automáticamente.
- El ensayo con `-batchmode` se conserva como `perf_batchmode_INVALID_FOR_GPU.json`: **no válido para evaluar FPS/renderizado**, aunque informe Direct3D11. No usarlo como aceptación de rendimiento.
- La ejecución normal con ventana oculta completa S1 durante 62 s, sin excepciones en el log, pero también devuelve tiempos incompatibles con una medición gráfica útil (0.62 ms de mediana). Se conserva como `perf_hidden_INVALID_FOR_GPU.json`; **rendimiento gráfico pendiente de comprobar con ventana visible**. No se afirma que cumpla el presupuesto de 30 FPS.
- La ejecución registra un intento de CP-00 rechazado por escritura en curso. No afecta a la terminación del recorrido, pero requiere revisión separada si se reproduce en una partida normal.
- Las tres partidas previas se respaldaron y restauraron; hashes SHA256 coincidentes después del ensayo. `source-hashes.json`, `working-tree-at-build.txt` y `tests.json` identifican las fuentes y validación; no representan un commit limpio.
