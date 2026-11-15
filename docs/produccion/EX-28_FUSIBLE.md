# EX-28 · Fusible del tablero

OBJ-010 FusibleModulo: fuente Blender, export FBX, atlas PBR de 512 px y prefab Unity. Modelo original con cuerpo cerámico biselado, hombros aislantes, dos terminales de pala, contacto usado, zapata posterior y etiqueta NEMESIS / F-010 / 16 A / LZ 0417. El texto forma parte del atlas.

360 triángulos y 200 vértices de fuente; una malla, un material y un set de texturas. Medidas Blender X/Y/Z: 0.08 × 0.0385 × 0.12 m, frente a objetivo 0.08 × 0.04 × 0.12 m. Se conserva origen inferior. Sin collider, audio, pickup ni minijuego, de acuerdo con la ficha.

Validación realizada en Unity: topología importada de 360 triángulos, conversión de ejes con error máximo cero, dimensiones y origen a tolerancia 0.1 mm, atlas 512 × 512 y ausencia de collider/interacción. Captura neutral revisada visualmente con serial legible. Consola sin errores. Evidencia en `SourceArt/_evidence/EX-28/OBJ-010_FusibleModulo`, incluido `validation.txt`. No se ejecutaron nuevas suites ni build para esta entrega de prefab sin cambios de lógica o escenas; las cifras EX-27 siguen siendo las de aquella entrega.

Estado: **Prefab validado**, no Conforme. Pendientes: alojamiento y montaje en OBJ-009, lectura a distancia de juego bajo iluminación regional y revisión artística final del desgaste. OBJ-009 y OBJ-033 continúan pendientes.

Contexto de integración comprobado: `Mechanism.Interact` ya concede permisos con `ObjectiveService`, registra `MechanismUsed`, emite ruido y reproduce palanca/relé. El plano identifica `MECH-LEVER-S1` y `MECH-PANEL-A`. Sus identidades y comportamiento deberán conservarse al reemplazar la representación visual; no se requiere inventar otro puzzle de fusibles.
