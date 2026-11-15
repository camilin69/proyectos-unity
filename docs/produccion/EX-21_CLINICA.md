# EX-21 · Equipamiento clínico

Cuatro fuentes Blender originales con FBX, UV, atlas PBR 1024 y prefab. Se trabajó mediante Blender MCP conservando escenas previas. La revisión visual movió los travesaños del lavamanos fuera de la cubeta y redujo la densidad de barras/biseles de la rejilla antes de los bakes finales.

| Ficha | Modelo | Triángulos | Dimensiones X/Y/Z de Blender |
|---|---|---:|---|
| OBJ-047 | SoporteFluidos | 4684 | 0.548 / 0.576 / 1.692 m |
| OBJ-049 | BandejaInstrumental | 1588 | 0.50 / 0.35 / 0.06 m |
| OBJ-051 | LavamanosIndustrial | 3232 | 0.80 / 0.618 / 0.900 m |
| OBJ-052 | RejillaDrenaje | 772 | 0.60 / 0.20 / 0.0377 m |

El soporte tiene base de cinco radios, ruedas, eje telescópico, ganchos, bolsas ficticias selladas y líneas con terminales protegidos. Su diámetro circunscrito es aproximadamente 0.6 m; la caja X/Y no es cuadrada. La bandeja tiene paredes y borde con espesor, pinzas de siluetas distintas y una sonda curva. El lavamanos tiene cubeta abierta de doble superficie, abertura de drenaje, grifo, sifón y conexión mural. La rejilla tiene láminas con espesor y colisión continua caminable.

## Montaje

ClinicalPlacement sustituye M059 por dos carros sanitarios existentes y coloca una bandeja sobre cada uno, con su base a 0.799 m. Añade el soporte junto a M056, el lavamanos contra el muro este y el drenaje delante. El punto de conexión mural se calcula por raycast. La posición final del lavamanos es (223.682,-8,58), aproximadamente. Se añadieron obstáculos de navegación con carving para lavamanos y soporte. Su recorrido con enemigos necesita observación en Play Mode.

El grupo Clinic_EX21 conserva el montaje en la regeneración de REG-S3. Aplicar de nuevo devuelve cero cambios y deja REG-S1 limpia. No se modifican identidades ni cantidades de pickups.

## Validación y pendientes

68/68 Edit Mode, 1.69 s, job a89cd4b7a0964b3cb40356036fe29088. Los cuatro casos nuevos verifican dimensiones, apoyo de origen, materiales con mapas y política de colisión. FurnitureReview comprueba muestras de vértices y topología contra Blender. Los cuatro imports tienen un submesh cada uno.

Capturas de prefab y de sala revisadas en SourceArt/_evidence/EX-21. La auditoría de colisiones detectó únicamente 32 mm de penetración entre la rejilla empotrada y Floor: el cuerpo queda bajo el suelo y su superficie superior sobresale unos 6 mm. Es intencional para la superficie caminable, pero el suelo provisional tapa el canal interior; falta abrir el hueco visual conservando la colisión de suelo. No se presenta esta inserción como acabado final. El diagnóstico global de albedo revisa 47 atlas sin detectar el defecto de metal negro.

Build Windows EX21-Clinical: Succeeded, 277.4 MB, 23.66 s, cero errores y una advertencia. Job build-c74bdd5df8; informe docs/produccion/evidencia/build_EX21-Clinical.json. Incluye el montaje clínico de esta entrega.

El soporte excede la referencia geométrica del GDD (4684 frente a 1500 tris); el lavamanos excede ligeramente 3000. Requieren optimización/LOD y revisión antes de aceptación. Los atlas 1024 de soporte, bandeja y rejilla también deben ajustarse a sus objetivos 512. Bandeja (1588/2000) y rejilla (772/800) están dentro de su referencia geométrica.

Otros pendientes: conexión del soporte a la bomba OBJ-046, desgaste localizado y marcas legibles, humedad/goteo y audio si se activa el suministro, integración visual del canal con el suelo e iluminación final. Todas las fichas están Integradas con acceptance_proven=false. La última suite completa de Play Mode es la de EX-20 (39/39), anterior a este montaje; no se atribuye a los cambios nuevos de escena. El objetivo de las 101 entradas sigue activo.
