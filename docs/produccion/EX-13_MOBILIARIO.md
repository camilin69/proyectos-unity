# EX-13 · Mobiliario original integrado

Siete fuentes originales, siete prefabs validados y 32 módulos en diez ubicaciones de S2/S4. El objetivo nocturno EX-12 sigue activo: el inventario contiene 101 entradas y quedan modelos, estados y acabado artístico pendientes.

| Ficha | Modelo | Triángulos | Uso |
|---|---|---:|---|
| OBJ-017 | BancoTrabajo | 4 296 | M023: tres puestos con mordaza |
| OBJ-018 | Mordaza | 2 300 | Prefab disponible; versión incorporada al banco |
| OBJ-028 | EstanteriaIndustrial | 4 104 | M025, M030, M031: once módulos |
| OBJ-030 | ContenedorTecnico | 1 732 | M022 y M039 |
| OBJ-038 | MesaOficina | 1 600 | M027 |
| OBJ-039 | SillaUsada | 3 856 | M029 |
| OBJ-072 | RackControl | 11 280 | M063/M064: catorce racks |

Cada prefab usa un mesh/submesh, un atlas y cuatro mapas PBR 1024. Unity empaqueta Metallic/Roughness para URP. Las fuentes conservan materiales editables y mapas empaquetados. Es un bake de materiales procedurales sobre UV, no de escultura high/low.

## Correcciones

Se separaron las superficies coplanares de la mesa de oficina, eliminando una mancha diagonal. Se redujo Pointiness durante el horneado para conservar pintura, madera y goma: EEVEE no mostraba el mismo aclarado que Cycles.

El origen exportado queda en el suelo mediante una copia temporal de mesh con matriz aplicada. Se conserva el origen editable. Las muestras de vértices confirman Blender (x,y,z) → Unity (x,z,y); cada axis_conversion.json registra el error máximo.

Las colisiones compuestas dejan libres los huecos y bloquean tableros, cajoneras y cargas. Los frentes miran hacia las zonas de uso; no se estiraron modelos para rellenar las huellas.

## Validación

- **36/36 Edit Mode** finales: job f9fbd59f056a4b4d8127153fbf4ef1d6. Incluyen siete contratos de prefab/material/origen y tres pruebas de rayos por huecos/cuerpos sólidos. Informe: SourceArt/_evidence/EX-13/final-edit-mode-tests.json.
- **Diez ubicaciones auditadas**: placement_audit.csv confirma dimensiones dentro de las huellas y desfase respecto al suelo 0.0000 m en todas.
- **Build EX13-Furniture: Succeeded**, 202 MB, 29 s, cero errores y una advertencia de com.unity.pipeline por falta de RuntimePipelineConfig. Informe: docs/produccion/evidencia/build_EX13-Furniture.json. El SHA de base no identifica todos los cambios locales.
- El comportamiento de captura mantiene la validación EX-12 de 38 pruebas Play Mode. Esa suite no se repitió en EX-13, que modifica arte estático y herramientas de integración.

Se conservaron posiciones corregidas, pickups y soportes existentes. No se rebakeó NavMesh ni se midió rendimiento nuevo: la auditoría de huellas no sustituye esas comprobaciones.

Cada carpeta SourceArt/_evidence/EX-13/OBJ-* incluye geometría, muestras de coordenadas, mapas, importación, conversión de ejes y captura neutral Unity. M023_in_game.png, M027_in_game.png, M030_in_game.png y M063_in_game.png muestran las salas reales. Los soportes y otros elementos provisionales siguen visibles: no se certifica acabado final de las salas.

## Reproducción y recuperación

Ejecutar build_industrial_furniture_ex13.py mediante Blender MCP: build(id), render(id), finish(id). export(id) reexporta sin repetir el bake. La exportación usa un submesh y STRIP, sin generar carpetas FBM.

En Unity: FurnitureReview.Integrate(asset), Capture(asset) y FurniturePlacement.ApplyExistingRegions(). FurnitureBuilder conserva esta colocación al regenerar el nivel. La actualización se detiene ante una escena abierta con cambios sin guardar.

La sesión original de Blender dejó de responder al MCP. Se conservó abierta y se continuó en una segunda instancia aislada, puerto 9877, con copia temporal del complemento. blender_mcp_client.py llama al servidor MCP instalado mediante stdio; no ejecuta bpy en Python externo. Registro: mcp-recovery.log. La configuración permanente y el complemento del usuario se conservaron.

## Pendiente

Corrección posterior EX-14: se regeneró el BaseColor de los siete modelos para conservar el color metálico y se actualizaron prefabs y capturas neutrales. La build EX14-Workshop incluye esta corrección; la build EX13-Furniture registrada arriba es anterior. Véase EX-14_TALLER.md.

Estados Integrado/Prefab validado, nunca Conforme. Falta desgaste localizado según cada ficha, aceptación artística con iluminación definitiva y, en el rack, estados visuales/ventilación ligados a EVA y revisión de LOD/rendimiento. La mordaza independiente no está colocada por separado en el nivel.
