# EX-49 — OBJ-002 Cámara vacía dañada

Se produjo una variante fuente-bloqueada de `OBJ-001_Criocamara` con la misma escala y lenguaje de construcción. La pieza focal incorpora una esquina de tapa forzada, vidrio ausente con cuatro fragmentos gruesos retenidos, cierre doblado, metal expuesto y la huella del sujeto anterior sobre el lecho. No es una recoloración del modelo intacto.

La tapa tiene un intento único de apertura de unos 2 segundos (`Cryo_Damaged_Jam`) y queda estable a 48 grados. `DamagedCryoSequence` activa el intento al acercarse el jugador, reproduce la firma sonora de motor y metal final, y mantiene la pose sin bucle. La escena `REG-S1` usa esta variante en `M011`.

## Entrega

- Fuente: `SourceArt/Blender/OBJ-002_CamaraVaciaDanada.blend`
- Exportación: `EsneiderProtocoloLazaro/Assets/_Game/Art/Models/OBJ-002_CamaraVaciaDanada.fbx`
- Prefab: `EsneiderProtocoloLazaro/Assets/_Game/Prefabs/Environment/OBJ-002_CamaraVaciaDanada.prefab`
- Evidencia: `SourceArt/_evidence/EX-49/OBJ-002_CamaraVaciaDanada`
- Geometría: 10.676 triángulos, 27 piezas
- Texturas: un atlas PBR de 1024 px con BaseColor, Roughness, Metallic y Normal
- Dimensiones: 2,7844 × 1,15915 × 1,08461 m
- Colisión: volumen raíz estable; las astillas pequeñas quedan decorativas

## Validación

Las pruebas EditMode comprueban geometría, piezas de daño, clips, collider, componente y sustitución de `M011`. La prueba PlayMode comprueba que el intento se reproduce una sola vez, alcanza el final y mantiene la tapa en la pose dañada. La aceptación artística permanece abierta hasta revisar la integración con la iluminación final de `REG-S1`.
