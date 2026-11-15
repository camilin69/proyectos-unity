# EX52 — Pantalla y primera persona

- Windows inicia en pantalla completa sin bordes, con resolución nativa. Se permite redimensionar la ventana y alternar con Alt + Enter.
- Ajustes incluye Pantalla completa y conserva la elección en PlayerPrefs, fuera del checkpoint. El editor y las ejecuciones `-autotest` conservan sus dimensiones.
- PICK-F01 y su carro se trasladaron a (12, -24, 12), dentro de S1-R01, junto al punto donde termina la apertura. Se conserva la identidad persistente del pickup. Actualizados la escena, el plano y la colocación del generador.
- Brazos: offset de cámara de (0, -0.32, 0.28) a (0, -0.27, -0.08), ocultando los extremos cortados detrás del encuadre. Las armas conservan sus anclajes a las manos.

## Validación

- Sin errores de compilación en consola.
- PlayMode: GameplayRepairPlayTests y SyringeViewmodelPlayTests, 4/4 aprobadas. Job `22c63de334dd4ce489993bdccdd07e21`.
- Lectura de la preferencia de pantalla en ambos estados verificada; configuración del player: FullScreenWindow, resolución nativa y ventana redimensionable.
- Encuadre observado en Game view: `Captures/EX52/arms-before.png`, `arms-after.png`, `arms-equipped.png` dentro del proyecto Unity.
- La transición de pantalla completa en Windows requiere ejecutable; no se considera validada visualmente desde Game view.

Ejecutable: `Builds/EX52-Fullscreen/EsneiderProtocoloLazaro.exe`.
