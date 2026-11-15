# EX-42 · Consola de preservación

OBJ-003 modelada e integrada en M002 de REG-S1. Sustituye visual y colisión del terminal genérico anterior, que queda desactivado. El modelo nuevo se mantiene a escala 1 y conserva la posición `(4,-24,12)` y orientación hacia el interior de la sala.

## Entrega

1568/3000 triángulos, dimensiones 0.70 × 0.45 × 1.1954 m en Blender XYZ. Pedestal, base, apoyos de goma, carcasa inclinada 20 grados, pantalla, tecla, tres lentes, tapa de servicio, tornillos, rejilla posterior, conexión tapada y retén. Un atlas PBR 1K con cuatro mapas; la tipografía usa el material compartido WorldSign. Fuente `SourceArt/Scripts/build_preservation_console_ex42.py`, .blend y FBX propios.

Dos cajas sólidas simplifican el housing; la pantalla no tiene trigger ni collider adicional. La consulta del jugador encuentra IInteractable en el mismo cuerpo. Sonido de relé local a volumen 0.06 y alcance 3 m al confirmar.

PreservationConsole lee OPENING_DONE del registro de sesión. Antes muestra diagnóstico/apertura pendiente; después muestra LÁZARO / ESNEIDER, tiempo transcurrido y 2000 AÑOS. Una confirmación establece PRESERVATION_RECORD_CONFIRMED; la segunda no genera otro evento. El estado proviene del snapshot restaurado, sin un vídeo o bucle independiente. También se actualiza si se restaura un checkpoint anterior con la consola ya cargada.

## Validación

115/115 Edit Mode, job `0bfc79ae5cf045ef8fe69111e02eef7a`, 3.8697257 s. Comprueba dimensiones, presupuesto, encaje de texto, inclinación y política de colisión/interacción.

1/1 Play Mode específico, job `7199024cf55145b1b6ddecb4fae5af3f`, 0.0672082 s. Comprueba diagnóstico, transición automática al flag de apertura, confirmación única y recuperación desde snapshot tanto con instancia nueva como existente. No simula toda la secuencia de apertura ni un guardado a disco.

Capturas de prefab y regionales a altura 1.65 m revisadas: texto de diagnóstico y de 2000 años legible a unos 1.1 m de aproximación, sin escalar el modelo. Evidencia y XML en `SourceArt/_evidence/EX-42/`.

Build Windows EX42-Preservation: Succeeded, 452.78 MB, 37.21 s, cero errores y 55 advertencias. Recibo en `evidencia/build_EX42-Preservation.json`. Este resultado no sustituye el recorrido jugable completo.

## Pendiente

Desgaste localizado en la tecla, indicadores con estado visual, ventilador localizado y click específico, conexión exterior con destino y recorrido de apertura completo con la cámara del jugador. La tecla confirma el registro pero no tiene desplazamiento mecánico animado. Falta LOD L-B según revisión de distancia. Integrado no implica aceptación final.
