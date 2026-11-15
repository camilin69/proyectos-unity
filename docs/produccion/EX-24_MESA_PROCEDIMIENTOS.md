# EX-24 · Mesa de procedimientos

OBJ-044 tiene fuente Blender, FBX y atlas PBR 1024, 3468 triángulos y un submesh. Dimensiones: 2.1 × 0.8217 × 0.9 m en Blender (ancho total incluye mandos de riel); dentro del presupuesto de 5k. Cuatro apoyos acolchados separados con bandejas, bordes y bisagras, columna telescópica con fuelle, eje de inclinación, actuador, base lastrada, cuatro pies niveladores, rieles y pedal recogido. La pose actual es neutra y estática, sin restricciones que atraviesen a un futuro sujeto.

Las ocho cajas de colisión cubren base, columna, espina y apoyos completos hasta la cara superior a 0.9 m; las juntas son visuales. El prefab incluye obstáculo NavMesh con carving. El movimiento autorado y su audio siguen pendientes de la escena correspondiente.

Sustituye las camillas OBJ-043 usadas provisionalmente en M056 (210, -8, 53) y M057 (219.67, -8, 64.17), conservando las posiciones corregidas existentes. Antes de sustituir se verificó que eran solo mallas y colisión, sin comportamientos adjuntos. FurnitureBuilder prefiere ahora OBJ-044 para la familia mesaq. ProcedureTableReview.ApplyExisting es idempotente: segunda ejecución, cero sustituciones.

Validación: coincidencia de triángulos y coordenadas Blender/Unity, revisión visual de prefab y ambas ubicaciones, 73/73 Edit Mode (job bf800fa306aa452bb748578069845979, 1.602 s). No se encontraron penetraciones superiores a 15 mm con mobiliario sólido. El barrido inicial sí devuelve EVT-15 y Volume_REG-S3 en edición: RoomEvent.Awake y RegionVolume.Awake los convierten explícitamente a triggers al iniciar; no se interpretan como mobiliario. La navegación efectiva de enemigos queda pendiente de recorrido jugable.

Build Windows EX24-Procedure: Succeeded, 288.55 MB, 21.68 s, cero errores y una advertencia; registro en evidencia/build_EX24-Procedure.json. No se atribuye un nuevo resultado Play Mode a esta entrega.

Pendientes: soporte y montaje de lámpara, brazo clínico, sujetos y manta, ajuste autorado y audio cuando proceda, desgaste localizado y revisión artística. La mesa está integrada, no Conforme. Evidencias en SourceArt/_evidence/EX-24. El objetivo completo sigue activo.
