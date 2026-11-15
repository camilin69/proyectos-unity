# EX-14 · Máquinas y utensilios de taller

Ocho modelos originales integrados en REG-S2, con fuentes Blender editables, FBX, atlas PBR 1024 y prefabs. El objetivo EX-12 sigue activo; esta entrega no completa el catálogo ni acredita aceptación artística final.

| Ficha | Modelo | Triángulos | Colocación |
|---|---|---:|---|
| OBJ-019 | Taladro fijo | 3056 | Suelo del taller |
| OBJ-023 | Bandeja de piezas | 2668 | Banco M023 |
| OBJ-031 | Bomba industrial | 5824 | Área M034, pieza de servicio |
| OBJ-032 | Generador local | 7300 | Sustituye volumen M034 |
| OBJ-034 | Válvula bridada | 3096 | Banco M023, repuesto |
| OBJ-035 | Extintor | 3036 | Soporte contra pared |
| OBJ-036 | Soldador con carrito | 4656 | Suelo del taller |
| OBJ-037 | Herramientas | 972 | Banco M023 |

Cada modelo tiene un submesh y material URP. Los colliders compuestos preservan los huecos relevantes; extintor y herramientas decorativas no añaden obstáculos. La regeneración mediante FurnitureBuilder conserva las nuevas colocaciones. No se modificaron reservas de pickups ni mecanismos del plan.

## Corrección del color metálico

El bake DIFFUSE/COLOR producía negro en superficies metálicas. esn_lib.bake_pbr ahora hornea BaseColor mediante emisión temporal del socket real del Principled, conservando y restaurando los enlaces de emisión originales incluso ante una excepción. Se regeneró BaseColor en los siete modelos EX-13 y los ocho EX-14; se conservaron Normal, Roughness y Metallic.

La regresión real ejecutada dentro de Blender verifica BaseColor enlazado, material metálico, color distinto de la emisión original, restauración de enlaces y limpieza del estado temporal. Resultado: passed, qa-pbr/regression.json. El diagnóstico de atlas deja 17 de 32 sin el problema amplio y señala **15 assets antiguos todavía pendientes de revisión/reparación** en METAL_ALBEDO_AUDIT.json. Este diagnóstico no sustituye aceptación artística.

## Evidencia y límites

- 47/47 Edit Mode aprobadas, job 1b771b08696d44fdae9539026a6cce9c. Incluyen dimensiones, origen, materiales, política de colisión y rayos sobre cuerpos sólidos. Informe: SourceArt/_evidence/EX-14/final-edit-mode-tests.json.
- Cero penetraciones contra obstáculos externos superiores a 15 mm. La distancia medida hasta la pared coincide con los 0.1055 m del soporte del extintor. Informe: placement_contacts.txt.
- Verificación Blender → Unity con muestras de vértices y revisión visual de las ocho capturas neutrales; vistas de taller, banco y generador dentro de la escena en EX14_workshop.png, EX14_bench.png y EX14_generator.png.
- Build EX14-Workshop: Succeeded, 230 MB, 20.2 s, cero errores, una advertencia por ausencia de RuntimePipelineConfig del paquete com.unity.pipeline. No es un fallo de URP. Informe: docs/produccion/evidencia/build_EX14-Workshop.json. El SHA base no identifica todos los cambios locales incluidos.
- Captura del Vigía conserva la validación EX-12 de 38/38 Play Mode; no se repitió esa suite para esta modificación de arte estático. No se midió rendimiento nuevo ni se rebakeó NavMesh.

Las salas conservan superficies y soportes provisionales. Faltan desgaste autorado, variantes y acabado con iluminación final. Bomba y válvula representan piezas de mantenimiento con puertos tapados; no se certifican conexiones funcionales, audio ni vibración del generador. Estados Integrado, nunca Conforme.

## Reproducción

Ejecutar build_workshop_machines_ex14.py mediante Blender MCP: build(id), render(id), finish(id), export(id). Batch.finish(id, only=('BaseColor',)) permite corregir únicamente el albedo conservando los demás mapas. El bake sigue siendo procedural sobre UV, no escultura high/low.

Integrar mediante FurnitureReview.Integrate(asset), capturar mediante FurnitureReview.Capture(asset) y colocar mediante WorkshopPlacement.ApplyExisting(). Las escenas abiertas con cambios sin guardar se protegen. El cliente blender_mcp_client.py mantiene el transporte MCP en la instancia aislada 9877 descrita en EX-13; la instancia original y configuración permanente se conservaron.

Skills aplicadas durante la entrega: flujo y armonización Blender, modelado, materiales, UV, exportación y revisión de renders; fundamentos, prefabs y pruebas Unity. Las skills ajenas a estos assets permanecen condicionadas al alcance correspondiente.
