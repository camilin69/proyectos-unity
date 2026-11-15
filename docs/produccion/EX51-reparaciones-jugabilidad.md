# EX51 — reparaciones de jugabilidad

Cambios motivados por la prueba del jugador:

- Barra permanente de seis casillas: varilla, pistola, escopeta, linterna, jeringas y raciones. Recoger otra arma conserva la selección actual.
- Brazos importados orientados hacia la cámara, clips de acción reiniciables y retroceso para armas de fuego. Indicador de impacto solo cuando se aplica daño.
- Golpe de varilla siguiendo el punto de mira, incluida la puntería descendente hacia el Vigía. Cápsula del Vigía ampliada a 1,36 m para cubrir la cabeza.
- Visuales de Vigía y Custodio girados 180° para alinear su frente importado (-Z) con navegación y percepción (+Z).
- Visión y emisión de proyectiles bloqueadas por cobertura. El sonido queda bloqueado si su recorrido incluye una pared, incluso si también cruza una puerta.
- Cierre de los ocho huecos exteriores entre las plantas de STA01 y STA02.
- Ocho Vigías adicionales: S1-R05, S1-R04, S2-R03, S2-R06, S2-R05, S3-R01, S3-R04 y S4-R01. Los dos de S1 se activan cuando se obtiene la varilla.
- Carteles e iluminación localizada en los armarios de PICK-W02 y PICK-W03.
- Eliminación de la luz direccional y los reflejos del cielo predeterminado en el interior. Iluminación reducida en S1-R05, S2-R05, S3-R04 y S4-R01; volúmenes correspondientes reducen el alcance visual enemigo. Luz separada mediante capas de renderizado para mantener visibles las manos sin iluminarlas con el haz de la linterna.
- Leer un documento abre inmediatamente una pantalla desplazable con el texto completo. Esc/cerrar devuelve el control.
- Dos sujetos adultos adicionales sustituyen cápsulas provisionales. Heridas que siguen el esqueleto y charcos de sangre en las celdas ocupadas.
- Restauración de checkpoint con vida máxima, inventario/documentos/puertas/enemigos/objetos guardados. Entidades de regiones exploradas después del guardado vuelven a su estado inicial. Cancelación de eventos pendientes y reinicio de su estado transitorio.
- Nueva partida recarga BOOT en modo Single y crea un registro de mundo nuevo. El menú conserva su confirmación para reemplazar un archivo existente y arranca directamente la secuencia inicial después de aceptarla.

## Regeneración

`RegionSceneBuilder` incorpora `EncounterRepair.ApplyRegion` y `CellHorrorRepair.Apply`; `BlockoutBuilder.BuildStairs` incluye los cierres. Para escenas existentes, las herramientas `GameplayRepair.Apply`, `EncounterRepair.ApplyExisting` y `CellHorrorRepair.ApplyExisting` son idempotentes y conservan las escenas ya editadas.

## Validación

Pruebas de integración añadidas en `GameplayRepairPlayTests` para visibilidad y dirección de manos/armas, conservación de armas, retroceso, daño a enemigos bajos, lectura inmediata y orientación/oclusión. `PersistencePlayTests` añade puertas, documentos, curación completa y entidades ausentes del snapshot. `MenuPlayTests.NewGameReloadsInitialWorldInsteadOfResumingProgress` usa los botones reales de nueva partida y confirmación, verifica la destrucción del jugador anterior y la limpieza del inventario, documentos, objetivos y guardado.

Se ejecutaron 128 pruebas EditMode sin fallos. La ejecución completa de 52 PlayMode encontró dos fallos: cambio de arma durante el retroceso y entrega de teclado sintético sin foco; ambos se corrigieron y sus pruebas posteriores pasaron. También se actualizaron las pruebas de sector para cerrar explícitamente la nueva interfaz de documentos. La última ejecución de cinco pruebas de nueva partida, reparaciones jugables y jeringa pasó completa. No se consideran válidos los intentos en que el descubrimiento del runner devolvió cero pruebas.

Capturas de revisión: `EsneiderProtocoloLazaro/Captures/EX51/`. Ejecutable: `Builds/EX51-GameplayFix/EsneiderProtocoloLazaro.exe`.
