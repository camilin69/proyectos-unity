# EX-40 · Brazo de reparación

OBJ-020_BrazoReparacion queda como prefab validado, todavía sin instalar en M024. No se declara aceptación final.

- Fuente: `SourceArt/Scripts/build_repair_arm_ex40.py` y `SourceArt/Blender/OBJ-020_BrazoReparacion.blend`.
- 2356/6000 triángulos, cuatro mallas rígidas y un atlas 1024 con BaseColor, Roughness, Metallic y Normal.
- Dimensiones Blender XYZ: 1.8125 × 0.48 × 1.355 m. Conversión FBX verificada mediante muestras de vértices.
- Pedestal anclado, largueros dobles, cuerpos y vástagos de actuadores, cables por segmento y pinza con dos apoyos.
- Prefab Unity con ShoulderPivot, ElbowPivot, WristPivot y ToolContact. Colisión únicamente en pedestal; partes móviles sin colisión.
- Pivotes Unity: hombro (0, .56, 0), codo (.72, 1.22, 0), muñeca (1.42, .95, 0). ToolContact (1.535, .631, 0) en reposo.

## Validación

112/112 pruebas Edit Mode, 0 fallos, 3.688506 s. Job `1bf4fc4ec6f04877bce62c72efa84e84`. XML en `SourceArt/_evidence/EX-40/EditMode-results.xml`.

La prueba del brazo comprueba jerarquía, anclajes, presupuesto, conservación de longitudes al articular y ausencia de IA. Capturas frontal, posterior y pose articulada revisadas en `SourceArt/_evidence/EX-40/OBJ-020_BrazoReparacion/`. Son vistas estáticas: no validan un ciclo animado ni contacto con el robot. No se ha ejecutado un nuevo build ni Play Mode en esta entrega.

## Pendiente

Componer el conjunto M024 con la plataforma EX-38, resolver la reserva espacial, contacto real de pinza y apoyos, ciclo de reparación, sonido y desgaste localizado. La pinza tiene dedos rígidos: apertura animada requeriría separar sus mallas. Revisar también interferencias de cables en el rango de movimiento final y colisión de partes móviles si quedan accesibles al jugador.
