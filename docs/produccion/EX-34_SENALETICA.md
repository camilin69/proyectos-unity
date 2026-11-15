# EX-34 · Orientación NAV-01–07 y placa de aislamiento

Ocho fuentes originales: los siete paneles NAV del apartado 87.2 y OBJ-016 junto a D06. Cada panel tiene chapa de 24 mm, tornillos, dos anclajes de suspensión y textos distintos en sus dos caras. Incluye nombres, pictogramas y flechas, sin depender únicamente del color. La placa de aislamiento tiene soporte mural, cuatro tornillos, impresión antigua NÉMESIS y placa EVA superpuesta que conserva legibles el sector y el contacto D06.

| Familia | Triángulos de fuente | Dimensiones Blender XYZ (m) | Texturas |
| --- | ---: | --- | --- |
| NAV-01–07 | 380 por panel | 2 × 0.034 × 0.652 | Un atlas PBR 1024 por nodo |
| OBJ-016 | 204 | 0.45 × 0.0365 × 0.30 | Un atlas PBR 1024 |

Las dos barras y sus dos placas de techo añaden 48 triángulos por nodo en Unity: 428 por conjunto suspendido. No tienen collider ni sonido. Los textos usan islas UV amplias reservadas; la ferretería ocupa otra zona del atlas. Los mapas son BaseColor, Roughness, Metallic y Normal. `esn_delivery.Batch.finish` acepta un margen opcional de bake; los demás consumidores conservan el valor previo de ocho píxeles y estos carteles usan dos.

## Texto y trazabilidad

`SourceArt/Scripts/prepare_navigation_ex34.py` toma puertas, escaleras y circulación del plano, genera las imágenes originales y escribe `Assets/_Game/Data/LevelPlan/navigation_signs_ex34.json`. El manifiesto conserva los 24 destinos, sus accesos, recorridos sobre cuadrícula de 0.5 m y flechas de ambas caras. La cara trasera invierte la dirección relativa al observador; no reutiliza una flecha frontal sin corregirla.

La búsqueda favorece recorridos cortos con pocos giros. La flecha representa el primer tramo sustancial de pasillo (al menos 4 m), evitando que una corrección corta de posición dentro del cruce indique una pared; si todos los tramos son menores, usa el inicial. No representa una ruta GPS ni revela enemigos, pickups o el mapa no descubierto. La comprobación independiente de coordenadas contra el GDD, continuidad de rutas y pertenencia a circulación queda en `SourceArt/_evidence/EX-34/routes_validation.json`. Esa prueba no sustituye comprobar obstáculos del mobiliario y comprensión del jugador.

## Montaje

Los paneles usan las posiciones NAV-01 P01 (16,16), NAV-02 P02 (20,20), NAV-03 P03 (27,30), NAV-04 P04 (22,26), NAV-05 P05 (20,28), NAV-06 P05 (46,28) y NAV-07 P06 (14,32). El borde inferior está a 2.4 m del suelo, con placa de 0.6 m de alto. NAV-01 mira hacia el sur por su cara frontal; los demás hacia el oeste. Las suspensiones llegan a techos encontrados mediante raycast. Se verifican ambas fijaciones antes de crear cada nodo.

OBJ-016 se coloca junto al marco D06 en S1 superior, a altura humana, sobre el muro x=40 y z=23.2. Sus apoyos traseros quedan a 0.5 mm del plano mural. Los contenedores de escena conservan posición/nombre independientemente del prefab importado para resistir regeneraciones del modelo. RegionSceneBuilder incorpora NavigationSignReview.

## Validación de entrega

Suite **100/100 Edit Mode**, trabajo `382dcaccea6c4e9c9147ed1405f227ba`, 3.4321456 s; XML nativo en EX-34. Las cuatro pruebas nuevas comprueban posiciones del plano, orientación, fijación de las dos suspensiones de cada nodo, ausencia de colliders y separación mural de OBJ-016. No se ejecutó nueva suite Play Mode: no se añadió comportamiento runtime.

Capturas de ambas caras de NAV-06, los ocho prefabs y montaje regional. La imagen de NAV-01 usa una aproximación de cuatro metros y la de D06 una vista cercana; todavía no constituyen un recorrido completo.

Build Windows **EX34-Wayfinding: Succeeded**, 350.74 MB, 20.70 s, cero errores y una advertencia. Registro en `evidencia/build_EX34-Wayfinding.json`. La reaplicación de montaje tras reimportar las texturas corregidas no modifica las escenas.

Las catorce capturas regionales frontal/trasera se toman a altura de ojos 1.65 m, a cuatro metros del panel, salvo la trasera de NAV-03 a 1.5 m para permanecer antes de la pared de oficina. Posiciones guardadas en `placements.tsv`.

## Pendientes de aceptación

Faltan señales de confirmación 3–5 m después de elegir, placas de autorización A/B y las placas de entrada/salida/numeración en curvas de conectores. OBJ-016 cubre la placa de aislamiento D06, no toda la familia de mensajes de emergencia. Hace falta recorrido con jugador por las 24 rutas, lectura desde ambas aproximaciones con iluminación final y desgaste localizado por montaje. Las fuentes/modelos no demuestran por sí solos aceptación de toda la sección 87. No se marca ningún nodo Conforme; el objetivo global sigue activo.
