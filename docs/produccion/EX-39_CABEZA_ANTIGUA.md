# EX-39 · Cabeza de Custodio antigua OBJ-022

Cabeza inerte original de 2048 triángulos, por debajo de 3000. Dimensiones Blender XYZ 0.300 × 0.2473 × 0.350 m, un mesh y un atlas PBR 1024 con cuatro mapas. Conserva del Custodio actual la carcasa marfil, ópticas pareadas, junta frontal y montaje cervical. La versión antigua añade una placa facial sustituible, lentes y aros separados, rejilla de voz, tapas laterales, ventilación posterior, brida y soporte de banco; el cable de servicio termina en un conector desconectado.

El diseño se comparó con la construcción de cabeza de `build_custodio.py`, sin ejecutar ese script, porque reinicia su escena. El script nuevo `build_legacy_head_ex39.py` conserva las demás escenas de Blender. El área protegida del rostro usa un polímero más limpio; el desgaste final localizado sigue pendiente de aceptación.

## Montaje

LegacyHeadReview coloca una única instancia sobre el primer módulo de banco M023, en `(108.15,-17.10,5.95)`, yaw 180, orientada al acceso. La primera colocación coincidía con la bandeja de piezas existente: se corrigió tras revisar la captura. `regional.png` conserva ese intento y `regional_fixed.png` muestra el montaje corregido. El soporte de la cabeza toca la superficie del banco; no tiene collider propio, Animator, mirada automática ni IA de enemigo. RegionSceneBuilder incorpora el montaje.

## Evidencia

Fuentes, geometría, atlas, comprobación de ejes, prefab y capturas en `SourceArt/_evidence/EX-39/OBJ-022_CabezaCustodioAntigua`. Prueba de escala/materiales/colisión y prueba de montaje que exige contacto con banco y ausencia de intersección con la bandeja. La bandeja se identifica por la malla importada, no por el nombre de instancia de escena.

Suite **111/111 Edit Mode**, trabajo `e34221c8e8eb42cab41648989d15d3e2`, 3.5461096 s, después de corregir la colocación. XML nativo en EX-39. La reaplicación no cambia la escena. No se ejecutó nueva suite Play Mode; este objeto no tiene comportamiento runtime.

Build Windows **EX39-LegacyHead: Succeeded**, 371.85 MB, 17.29 s, cero errores y una advertencia, con la colocación corregida. Registro en `evidencia/build_EX39-LegacyHead.json`.

## Pendientes

Falta el póster cercano de la versión anterior, acabado localizado y recorrido con iluminación final. El atlas es propio; aún debe consolidarse con otros elementos de taller cuando se prepare el atlas compartido previsto por la ficha. Estado Integrado, aceptación no probada. Objetivo global activo.
