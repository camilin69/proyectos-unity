# Checklist de la rúbrica — Taller Final

| Requisito | Cómo se cumple | Dónde comprobarlo |
|---|---|---|
| Terrain | Pradera (S2), colina del árbol (S3) y playa (S5) son `Terrain` con dos capas pintadas y pasos por capa | `SceneContractTests.LosTerrenosTienenCapasYSuperficies` |
| Skybox | Physically Based Sky de HDRP; el sol y la luna los mueve `TimeOfDay` de 07:00 a 00:00; de noche, cubemap de estrellas y estrellas fugaces | Boot → `Luz` y volúmenes `S4..S7` |
| Fog | Niebla volumétrica global y por escenario; el bosque de S5 se cierra con un volumen local; nubes volumétricas | `Settings/Volumes/*` |
| Personaje humanoide | El soñador: FBX propio con Avatar **Humanoid** válido, Animator de 9 estados | `AvatarTests` |
| Diagrama de animación | `Docs/Diagrama_Animator.png`, generado de la misma spec que construye el controller | `AnimatorMatchesSpecTests` (diagrama = implementación) |
| Entradas | WASD/flechas, ratón, Shift (trotar), Espacio (saltar/subir), E (recordar), Q (volar en S3), Ctrl (bajar), F (cámara de cine), Tab (saltar cinemática), Esc (pausa), Enter | `DreamInput` |
| Física: colliders y triggers | CharacterController con detección de suelo por SphereCast; triggers de recuerdos, pasos, agua, puntos seguros y volúmenes | `PlayerMotor`, `TransitionGate`, `WaterZone`, `Checkpoint` |
| Objetivo y progreso | Un recuerdo escondido por escenario abre el paso al siguiente; 8 escenarios | `JourneyPlayModeTests.SinElRecuerdoLaPuertaNoAbre` |
| Puntaje | 1000 por recuerdo + bono por rapidez (hasta 500); se cierra al final | `CoreRulesTests`, `ElViajeCompletoTerminaEnElCuartoAMedianoche` |
| UI | Pantalla inicial (título, objetivo, controles, vaivén y calidad), HUD (sueño, hora, recuerdos, puntaje), pausa, panel final «¿DESPERTASTE?» | `UI/*` |
| Sonido | Música en bucle sin costura tintada por escenario, pasos por superficie en el contacto real del pie, campanilla, zumbido de la luz, reverb por zona | `MusicPlayer`, `FootstepSystem`, `SfxPlayer` |
| Pantalla final | Vuelve al cuarto a medianoche y muestra recuerdos, puntaje y tiempo | `EndPanel` |

## Pruebas
- EditMode (26): spec ↔ controller, Avatar, reglas y contrato de cada escena.
- PlayMode (3): puerta cerrada sin recuerdo, ciclo de la tecla F, viaje completo de 07:00 a 00:00.
Ejecutar: *Window → General → Test Runner*, o `unity command test run`.
