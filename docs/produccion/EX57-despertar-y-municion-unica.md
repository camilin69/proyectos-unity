# EX57 — Despertar y contador único de munición

Sustituye la presentación de cargador/reserva de EX56 por el total único solicitado. Pistola y escopeta muestran «N balas» y «N cartuchos» en la casilla del arma y encima de resistencia. La munición no ocupa casillas ni se selecciona como objeto. Cada lote suma sus unidades aceptadas y cada disparo válido resta una. No existe recarga manual; R no altera acciones ni munición. Se retiró su indicación del menú de controles.

Para conservar los checkpoints existentes, los dos campos de munición del formato anterior siguen serializados y `Inventory.TotalAmmo` suma ambos. `ConsumeRound` puede gastar cualquiera de los dos directamente, sin barrera entre cargador y reserva. La migración de hotbar elimina las casillas antiguas de munición y conserva la selección del arma por identidad. Se mantienen los límites de recogida existentes y la recogida parcial.

`OpeningSequence` crea `WakeVision` al comenzar la apertura de la criocámara. Una malla uGUI con párpados curvos y bordes de alfa suave abre y cierra los ojos, mientras un fundido negro recupera progresivamente la visión durante nueve segundos. La subida existente de cámara continúa hasta entregar el control. HUD oculto durante la secuencia; al finalizar vuelve a mostrarse y el mensaje de 2000 años permanece seis segundos. E/Espacio omiten el efecto y la secuencia. La pausa congela la transición. Al desactivar la secuencia se elimina la capa y se restaura el estado previo del HUD. No usa desenfoques de pantalla ni texturas de render adicionales.

## Validación

- PlayMode 8/8: job `fa11e599fac340bf834cf4d95313e3dd`. Finalización natural, pausa, omisión con limpieza de capa y restauración del HUD, CP-00, ambos totales de munición, 10 + 10 = 20 y disparo = 19, disparo directo desde reservas de guardados anteriores, migración de selección, hotbar/checkpoint y colisiones de proyectiles.
- Captura de párpados verificada: `EsneiderProtocoloLazaro/Captures/EX57/waking-eyes-3.png`.
- Captura del contador encima de resistencia, sin casillas de munición: `EsneiderProtocoloLazaro/Captures/EX57/ammo-single-total.png`. Comprobado después un disparo válido y total 19.
- La primera revisión visual detectó que el Graphic personalizado necesitaba CanvasRenderer; corregido con RequireComponent, añadido a la prueba y verificado visualmente.
- Pruebas usan guardados temporales; capturas sin escribir checkpoints de producción.

Build Windows64 completada: job `build-fbe02caeb4`, 26,94 s, 223,13 MB, 0 errores y 61 advertencias.

Ejecutable: `Builds/EX57-WakeupAndAmmo/EsneiderProtocoloLazaro.exe`.
