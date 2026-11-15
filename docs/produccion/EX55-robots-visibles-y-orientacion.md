# EX55 — Robots visibles y orientación de ataque

## Causa y cambios

La revisión de las regiones encontró 23 Vigías con 37 SkinnedMeshRenderer antiguos sin `sharedMesh`. Esas piezas se habían sustituido en el FBX por dos mallas LOD; las copias antiguas de las escenas conservaban la IA y el collider, pero no podían dibujarse.

`RobotPresentationRepair` sustituye únicamente su hijo visual por el prefab vigente y renueva Animator/clips. Conserva EnemyBrain, posición, rutas, colisión e identidad persistente. Se inspeccionaron los 45 robots y se guardaron las regiones reparadas, incluidos los conectores C1–C3. La generación de enemigos nuevos ya usa el prefab vigente.

La cara importada apunta a -Z; el visual conserva la corrección de 180° respecto al +Z de juego. La orientación se verificó con clips, no sólo con la pose inicial. La IA ahora mantiene la cara hacia el objetivo visible al retroceder, desactiva el giro de NavMeshAgent durante preparación/ataque/recuperación y exige alineación de unos 15° antes de emitir. El Animator no usa root motion y sigue evaluando fuera de cámara.

## Validación

- EditMode: 3/3 aprobadas, job `b3549ab18b3945e8ae4d5998ef8e516c`. Mallas y huesos válidos en los 45 robots, referencias LOD válidas y orientación de la cabeza en los clips de Vigía y Custodio (excepto muerte).
- PlayMode: 4/4 aprobadas, job `6f603fec9cf44f38956e958cd6567ad7`. Ataque hacia atrás rechazado, ataque orientado permitido, cesión del giro de navegación, comportamiento de IA y visión bloqueada por paredes.
- Revisión visual en ejecución de V01, antes invisible: `Captures/EX55/v01-visible-facing.png` y `v01-lod1-visible.png` dentro del proyecto Unity. Ambas mallas de detalle se dibujan de frente durante la preparación.
- Custodio animado desde el frente de juego: `Captures/EX55/custodio-current-facing.png`.
- Una primera ejecución de EditMode falló al restaurar una escena temporal sin ruta; corregido el cierre de la prueba y repetidas sus tres comprobaciones.

Ejecutable: `Builds/EX55-RobotFix/EsneiderProtocoloLazaro.exe`.
