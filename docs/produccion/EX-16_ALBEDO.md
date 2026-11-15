# EX-16 · Reparación del albedo metálico heredado

La corrección del bake BaseColor de EX-14 se aplica a los quince assets antiguos señalados: tres robots, criocámara, banco industrial, carro, jaula, camilla, terminal, puerta corrediza, jeringa y cuatro armas/accesorios. El trabajo corrige el color perdido al hornear metales con DIFFUSE/COLOR; no acredita acabado artístico final ni completa los modelos restantes.

## Método

repair_legacy_albedo_ex16.py carga cada fuente en una escena separada, conserva sus UV y hornea el socket Base Color mediante emisión temporal. No vuelve a desplegar UV ni reexporta FBX. En el Vigía se hornean las 37 piezas editables de EX11_LOW, excluyendo las copias de exportación LOD0/LOD1. El atlas empaquetado compartido por esos LOD se actualiza con el resultado.

Cada asset conserva una copia de la fuente y del BaseColor anterior en SourceArt/_evidence/EX-16. Las huellas de geometría, UV, huesos y pistas NLA antes/después deben coincidir. Se comprueban además hashes SHA-256 de FBX, Normal, Roughness y Metallic antes de copiar el nuevo BaseColor al proyecto. Se restauran visibilidad, pose y escena activa de Blender. Se empaqueta el albedo nuevo en la fuente editable.

La inspección inicial de las quince fuentes detectó cero caras sin material, cero UV ausentes y cero materiales usados sin Principled. Los slots vacíos no usados que Cycles informa durante el bake no se confunden con caras sin material.

## Evidencia y alcance

Resultado final: quince reparaciones verificadas; los 35 atlas del proyecto pasan el detector de metales negros. Se verificaron nuevamente 60 archivos protegidos sin cambios. Las quince capturas Unity posteriores se revisaron individualmente y en tres hojas de contacto.

Build EX16-Albedo: Succeeded, 238 MB, 23.46 s, cero errores, una advertencia conocida de com.unity.pipeline por RuntimePipelineConfig ausente. Informe: docs/produccion/evidencia/build_EX16-Albedo.json. El SHA del informe es la base del repositorio y no identifica por sí solo los cambios locales incluidos.

SourceArt/_evidence/EX-16 contiene source-inspection.json, los recibos repair.json por asset, imágenes originales, capturas Unity posteriores y la verificación independiente de archivos protegidos. audit-before.json y audit-after.json permiten comparar el diagnóstico completo; ese criterio de píxeles metálicos negros es un detector de este defecto, no una prueba de fidelidad artística.

La suite existente pasa 47/47 Edit Mode (job 0e4e251b5dad4dc0afc00589bf252c5a). Esta suite cubre regresiones de prefabs y LOD; los hashes y la comparación de atlas verifican la reparación específica. No se repitió Play Mode: ningún FBX ni código de captura cambia en EX16.

FurnitureReview.Capture admite ahora ruta de prefab y directorio de salida opcionales para revisar actores, armas y props con iluminación neutral. Fuerza el LOD principal únicamente en su instancia temporal. La criocámara y el terminal aún necesitan su revisión de vidrio/pantalla y los robots su acabado autorado; la corrección de albedo no elimina esos pendientes.

Unity quedó detenido por el diálogo «The open scene(s) have been modified externally» después de la limpieza de whitespace de S1 al cerrar EX15. Se inspeccionó con la skill de control de Windows, se enfocó el diálogo y se recargó el archivo previamente guardado. Unity volvió a responder con REG-S1 limpia. Evitar nuevas escrituras externas sobre escenas abiertas: cualquier limpieza futura requiere cerrar primero la escena o gestionar explícitamente la recarga. No fue necesario reiniciar Unity ni Blender.

Reproducción: inspeccionar fuentes con inspect_all(); ejecutar repair(asset) dentro de Blender MCP. run_legacy_albedo_queue_ex16.py llama al servidor MCP instalado de forma secuencial y se detiene si falta un recibo o hay un resultado incierto. verify_legacy_albedo_ex16.py vuelve a comprobar archivos protegidos y construye hojas de contacto a partir de capturas reales.

El objetivo EX12 conserva las 101 entradas del inventario y continúa activo. No se cambia ningún estado a Conforme por esta reparación.
