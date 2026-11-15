# EX-33 · Cajas de munición y remanente persistente

OBJ-027 tiene dos variantes: CajaMunicionPistola (988 triángulos) y CajaMunicionEscopeta (812), dentro del presupuesto de 1000. Cada una usa dos mallas, caja y contenido, y un atlas PBR 512 con cuatro mapas. La caja nominal cerrada mide 0.3 × 0.2 × 0.15 m; el conjunto modelado, con tapa abierta a 110 grados y accesorios, ocupa 0.3 × 0.2921 × 0.3387 m en Blender XYZ.

La geometría incluye fondo y cuatro paredes, tapa con liner interior, junta de boca, bisagras, cierre y asa. Hay cartón con bandeja y munición visible, diferente por tipo, además de etiquetas EVA/PISTOLA o EVA/ESCOPETA en caja y paquete. Las etiquetas tienen islas UV reservadas para legibilidad. La primera importación mostró contaminación de colores en biseles: se aumentó la separación entre islas y se redujo el margen de bake a dos píxeles. `esn_lib.bake_pbr` admite ahora ese margen opcional, conservando ocho píxeles como valor anterior para sus demás consumidores. Los mapas y FBX finales se regeneraron.

## Integración y comportamiento

Se sustituyen las esferas visuales de **22 pickups**: cinco en REG-S2, once en REG-S3 y seis en REG-S4. Doce son munición de pistola de diez unidades; diez son munición de escopeta de cuatro unidades. Se conservan los componentes Pickup/PersistentEntity originales, IDs, GUIDs, tipos y cantidades. El registro de cada instancia está en `SourceArt/_evidence/EX-33/placements.tsv`.

Cada caja se apoya en el soporte existente asociado al ID. La esfera y su collider se sustituyen visualmente por el modelo y una caja de interacción simple; la carcasa no añade collider que tape el rayo. El pickup se aloja como hijo de una raíz visual independiente. Al agotarse, Pickup desactiva solo ese hijo; AmmoCaseVisual oculta el contenido y deja visible el envase vacío. La cantidad autoritativa sigue en Pickup y WorldStateRegistry. La geometría del paquete es una indicación de existencias, no un contador exacto durante una recogida parcial; el prompt conserva la cantidad exacta.

La reimportación del prefab invalidó inicialmente los overrides de posición de escena. AmmoCaseReview repara nombre, colocación y vínculo al pickup a partir del soporte conservado y registra los overrides nuevos. Las escenas se guardaron, recargaron y comprobaron; la segunda aplicación no modifica nada. RegionSceneBuilder incluye el montaje al regenerar regiones.

## Verificación

- Renders Blender y capturas Unity de ambas variantes revisados. Capturas adicionales del envase vacío y de A01/S01 en sus regiones.
- Pruebas de recogida parcial con capacidad limitada, inventario lleno sin consumo/eventos adicionales, restauración del remanente y restauración de una caja agotada sin volver a dar munición.
- Pruebas de las tres regiones: cantidad e identidad originales, altura de apoyo y rayo frontal que alcanza el pickup.
- **96/96 Edit Mode**, trabajo `25f4fd4d177c48bc879e0dd6de076a1a`, 2.2879848 s. XML nativo en EX-33.
- **1/1 Play Mode específico**, trabajo `5c9dc007ed9642bbb7333b548cee045b`, 0.0507458 s. Verifica la actualización automática de contenido después de desactivar el pickup y al restablecer existencias. No equivale a una nueva ejecución de toda la suite Play Mode.

Build Windows **EX33-AmmoCases: Succeeded**, 323.85 MB, 39.28 s, cero errores y 55 advertencias. Registro en `evidencia/build_EX33-AmmoCases.json`.

## Pendientes

Los soportes de bloque todavía deben reemplazarse por muebles definitivos apropiados a cada sala. Quedan desgaste localizado en cierre/asa, firma sonora breve de recogida y recorrido con jugador e iluminación final. Las capturas regionales demuestran apoyo y presencia, no aceptación artística final. Estado Integrado, aceptación no probada; objetivo global activo.
