# EX-11 · Refinamiento del Vigía

## Alcance y dirección

Continuación de EX-10. Se prioriza el enemigo base para establecer un flujo de geometría y LOD que después pueda aplicarse a los otros robots. Brazos y armas siguen pendientes.

Skills: blender-skill-harmonizer coordina; blender-modeling controla forma; blender-materials y blender-export controlan atlas y entrega; animation-quality-gate guía la revisión de poses importadas. La referencia es el diseño existente y el GDD: robot de contención bajo, cabeza grande sin boca, óptica no emisiva, torso encogido y antebrazos largos. No hay una hoja VIS aprobada ni se afirma fidelidad 1:1 a una imagen.

Se estrechan cintura y barbilla mediante deformaciones coherentes por grupo rígido, manteniendo alineados tornillos, rejillas y tapas. Se conserva el atlas existente; no se afirma un nuevo bake high→low ni texturizado autorado completo.

## Reproducción

- Entrada inmutable de esta iteración: `SourceArt/Blender/Archive/BOT-01_Vigia_EX10.blend`.
- Ejecutar `SourceArt/Scripts/refine_vigia_ex11.py` dentro de Blender mediante MCP.
- Fuente de salida: `SourceArt/Blender/BOT-01_Vigia.blend`, colecciones LOW, RIG y EXPORT con prefijo EX11.
- Exportación: el FBX canónico mantiene rig y nombres de clips; las piezas comparten un renderer por LOD y el atlas existente.
- `VigiaReview.Capture` genera capturas de prefab y clips en una escena temporal; no guarda cambios en las escenas del usuario.

## Validación

- LOD0: 18 614 triángulos, 9 705 vértices. LOD1: 8 562 triángulos, 4 679 vértices (54 % menos triángulos). Un submesh por nivel; se dibuja un nivel cada vez. El recuento de 27 176 del importador suma ambos y no representa triángulos simultáneos.
- Rig compartido de 17 huesos, cero vértices sin pesos. Clips importados con los cinco nombres originales. La segunda ejecución desde la base reproduce los mismos recuentos.
- Material URP: intensidad de normal 0.3 y escala de smoothness 0.45 para moderar el brillo y el relieve del atlas existente.
- LODGroup cambia a 18 % de altura proyectada y oculta por debajo de 1.5 %. Bounds de skin calculados muestreando los cinco clips, con 8 cm adicionales; la prueba comprueba que las poses quedan contenidas. Falta validar perceptualmente la transición en una partida visible.
- Blender: pasan G-01, G-02, G-03, G-04 y G-06. Marcha implícita 0.68 m/s; despeje mínimo 79.6 mm. Informe `SourceArt/_evidence/EX-11/contacts_BOT-01_Vigia.json`.
- Unity: suite Edit Mode 26/26 (job `caceba8a9e2e469ab0fb88bfe3823160`), incluidos deformación de ambos LOD, rig compartido, bounds y contactos importados. Play Mode: 3/3 de EnemyAiPlayTests y CampaignRunPlayTests (job `31695b926e7f4b4997a1f696e6c0548a`). Se trata de pruebas automatizadas; no certifican una partida manual completa.
- Tras regenerar desde la base: 2/2 pruebas de LOD y marcha aprobadas (job `74019a2cb6d44d289f736524f4959c8f`).
- Build Release `EX11-Vigia`: Succeeded, 167 MB, 26.74 s, cero errores y una advertencia. Informe en `docs/produccion/evidencia/build_EX11-Vigia.json`. Contiene los cambios locales de esta tarea y los que ya existían: el commit base no describe un árbol limpio. No se ejecutó un nuevo benchmark gráfico.
- Evidencia: `before_back_iso.png` / `final_back_iso.png` comparten cámara; `final_front.png`, `final_iso.png` y `final_LOD1.png` muestran la entrega. Los archivos iniciales `before_front.png` y `before_iso.png` muestran la espalda: el eje frontal se corrigió después en el capturador.
- `contact_sheet.png` revisa cuatro fases de marcha, preparación, disparo y caída. No hay piezas separadas ni recorte del sujeto en las muestras; no equivale a una revisión continua de todos los fotogramas.
- La limpieza recursiva de `Assets/_Game/Art/Models/BOT-01_Vigia.fbm` fue rechazada por la revisión automática. Se conserva sin referencias desde el prefab; la exportación reproducible ahora usa STRIP para no volver a copiar las texturas.

## Pendientes

Este cambio mejora proporciones y coste de renderers; no cierra el acabado Tier A. Faltan una dirección visual VIS aprobada, textura de desgaste con intención, refinamiento facial/anatómico más profundo y revisión de las transiciones LOD en juego. No se declara ninguna mejora medida de FPS. La build EX10-S1 anterior no contiene este Vigía.
