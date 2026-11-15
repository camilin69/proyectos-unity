# EX56 — Munición, disparos y escopeta

La casilla de balas/cartuchos ahora muestra el total del inventario (`cargador + reserva`), calculado por `Inventory.TotalAmmo`. Cada disparo válido lo reduce una unidad; recargar únicamente transfiere munición. El HUD distingue cargador y reserva y muestra «R · Recargar» al vaciar el arma con reserva disponible. La recogida de pistola/escopeta conserva y suma la munición obtenida antes, limitada por la capacidad de reserva existente. No cambia el formato de guardado.

`PlayerActions.Fired` comunica los impactos resueltos a `WeaponFireVisual`: destello, iluminación breve, estelas que terminan en la cobertura alcanzada y movimiento de corredera en la pistola. Las dos armas emiten efectos solo tras consumir munición. Se usa la boca del modelo equipado y un material Resources incluido en la build. Los efectos son cosméticos; el daño continúa resolviéndose una sola vez por hitscan. Se mantienen clic izquierdo para disparar, clic derecho para linterna y R para recargar.

Los proyectiles enemigos resuelven solapamientos al inicio de cada paso, además del barrido del trayecto. Esto cubre al jugador que entra en la esfera entre pasos físicos. Ignorar al emisor ya no descarta el resto del barrido. Las paredes siguen interceptando los proyectiles y se conserva la invulnerabilidad breve tras daño y la deduplicación por AttackID.

La escopeta existente es `PICK-W03`, en el armario de Seguridad (`S3-R05`, clínica B-2). `WeaponCabinetFacing` gira el armario hacia la entrada norte y conserva la posición relativa del arma, sus colliders y su identidad persistente. Aplicado a REG-S3 y a su generador; no se duplicó la recogida. E abre el armario y, apuntando al arma, E la recoge.

## Validación

- PlayMode: 7/7, job `488de2dfde7247ad816ace7269380bbd`: munición recogida antes del arma, total después de disparar y recargar ambas armas, efectos ausentes al disparar en vacío, estelas detenidas en paredes, hotbar/checkpoint, colisión con vidrio, impactos rápidos y con solapamiento, cobertura y vida 90 → 60 → 30 → 0 por tres proyectiles de Custodio.
- EditMode: 4/4, job `597cb385cc744fefa03cfdf3992912b7`: apertura de armarios de campaña y raycast de interacción que alcanza las armas al abrirlos, incluida la escopeta reorientada.
- Capturas revisadas: `EsneiderProtocoloLazaro/Captures/EX56/pistol-shot.png`, `pistol-slide.png` y `shotgun-access.png`.
- Pruebas y capturas sin escribir checkpoints de producción. Editor restaurado a REG-S1.

Build Windows64 completada: job `build-c6f870fd55`, 60,37 s, 223,13 MB, 0 errores y 61 advertencias.

Ejecutable: `Builds/EX56-AmmoAndFire/EsneiderProtocoloLazaro.exe`.
