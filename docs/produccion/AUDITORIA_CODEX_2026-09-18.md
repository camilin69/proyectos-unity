# Auditoría de estado — Codex · 2026-09-18

## Conclusión

El proyecto ya contiene una campaña funcional completa y una base técnica extensa. El principal trabajo pendiente es elevar la presentación visual: modelos Tier A, texturas, materiales del entorno, iluminación, LOD y sustitución de placeholders. La evidencia actual permite afirmar que existe un juego ejecutable, pero no que haya alcanzado el acabado visual P2 definido por el GDD.

Esta auditoría inspeccionó el repositorio, los documentos de producción, la evidencia, la build registrada y los 16 archivos `.blend` mediante Blender 5.2.1 en modo lectura. No modificó assets ni escenas.

## Implementado y respaldado por archivos

- Proyecto Unity 6000.6.1f1 con URP 17.6, Input System, AI Navigation y Test Framework.
- Campaña S1 → C1 → S2 → C2 → S3 → C3 → S4 → exterior, distribuida en BOOT y siete escenas regionales.
- Movimiento en primera persona, resistencia, agacharse, salto, interacción, tres armas, linterna, curación e inventario.
- Vigía, Custodio y Archivista con percepción, navegación, estados y combate; jefe con fases y ataques.
- Objetivos O01–O11, eventos narrativos, documentos, puertas, mecanismos, checkpoints, derrota, victoria y escape.
- Guardado transaccional, recuperación de backup, persistencia de entidades y streaming regional.
- Menús, HUD, mapa, documentos, opciones de accesibilidad y ajustes persistentes.
- 91 archivos WAV, materiales URP, 16 FBX, 16 fuentes Blender, 19 prefabs y pruebas EditMode/PlayMode.
- Evidencia registrada: 25 pruebas EditMode y 35 PlayMode aprobadas en la última ejecución documentada.
- Rendimiento documentado en el equipo local para 720p/30; los seis tramos medidos cumplen el presupuesto registrado.

## Hallazgos que impiden considerar el arte terminado

### 1. Los assets focales siguen siendo una base procedural

Los 16 `.blend` se abren correctamente y contienen geometría, materiales y, cuando aplica, rigs y acciones. Sin embargo:

- Ninguno presenta una estructura real de colecciones `HIGH`, `LOW`, `RIG`, `EXPORT`, `REFERENCES` y `COLLISION` como exige el GDD.
- No hay objetos LOD identificables en las fuentes.
- Las imágenes de textura no están enlazadas o empaquetadas en los `.blend`; el horneado vive fuera de la fuente.
- La documentación confirma que no hubo escultura high→low ni texturizado pintado con intención.
- Las capturas de juego muestran superficies planas, espacios grandes con poco detalle, iluminación uniforme y escasa separación visual.

Inventario directo de las fuentes principales:

| Asset | Tris en `.blend` | Bones | Acciones | Diagnóstico |
|---|---:|---:|---:|---|
| BOT-01 Vigía | 18 614 | 17 | 5 | Silueta legible; anatomía mecánica, rostro, articulaciones, textura 2K y LOD pendientes |
| BOT-02 Custodio | 21 096 | 17 | 6 | Volumen funcional; por debajo del acabado Tier A y sin LOD |
| BOT-03 Archivista | 34 600 | 17 | 7 | Jefe funcional, pero justo por debajo del rango local y lejos del perfil de alta fidelidad |
| CHR-01 brazos | 21 480 | 33 | 5 | Agarre medido; anatomía, piel, uñas, deformación y materiales de primer plano requieren mejora |
| OBJ-001 criocámara | 9 964 | 4 | 2 | Prop focal funcional; falta high→low, desgaste autorado, vidrio final y gesto de huella |
| Pistola / escopeta | 7 164 / 10 952 | 0 | 0 | Funcionan como piezas rígidas; requieren acabado de viewmodel, piezas móviles y texturas 2K |

### 2. El entorno conserva calidad de blockout

- El exterior está construido y es transitable, pero visualmente sigue en blockout+: terreno plano, torres simples, sin vegetación, ruina ni composición atmosférica final.
- El kit de mobiliario regional usa materiales planos y no tiene LOD.
- Los grandes paños de suelo, paredes y techo carecen de variación, trims, decals, suciedad localizada y detalles de construcción suficientes.
- El vidrio M060 permanece opaco.
- Falta fabricar la señalética NAV-01…07.
- Las 19 hojas VIS de la sección 82 siguen pendientes, por lo que no hay una referencia visual aprobada contra la cual cerrar los assets.

### 3. Aún hay placeholders dentro de escenas de campaña

- Cinco sujetos humanos de jaulas son cápsulas placeholder.
- El gabinete CP-06 sigue identificado como placeholder.
- Persisten prefabs de Vigía y Custodio placeholder para el sandbox.
- Algunos soportes de pickups se generan como geometría provisional.

Los humanos focales son una carencia especialmente visible porque el GDD exige anatomía, ropa, injertos y variación de poses para sostener el horror ambiental.

### 4. La animación funcional aún necesita una pasada artística

- Los contactos de marcha y agarre están medidos y pasan sus pruebas.
- Falta el giro de cabeza de patrulla.
- Falta el gesto/huella al abrir la criocámara.
- Ataques, impactos, tambaleos y muertes no tienen un gate visual equivalente al de la marcha.
- Los rigs de los robots tienen 17 huesos, suficientes para el sistema procedural actual, pero limitados frente al objetivo del GDD para deformación y actuación Tier A.

### 5. La build Release no representa el estado actual

`docs/produccion/evidencia/build_Release.json` apunta al commit `72328dd`, anterior a los commits EX-09. El repositorio está en `bfa624d` y además contiene cambios locales en jugador, menú, prefab y showcase. Por ello:

- la build entregable no certifica las últimas mejoras de assets, contactos, exterior y física;
- las pruebas documentadas no certifican todavía los cambios locales actuales;
- se debe regenerar y volver a medir la build después de cerrar o apartar esos cambios.

## Pendientes funcionales y técnicos

- Reacción física de props ante golpes de varilla y disparos.
- Evitar que una puerta atraviese un carro al cerrarse.
- Prueba automática de una ruta completa de sigilo.
- Casos de guardado con GUID duplicado y disco sin espacio.
- Migraciones reales entre versiones del esquema de guardado.
- Compatibilidad con mando.
- Medición de 1080p/60 y captura de profiler Development.
- Prueba reproducible desde una copia limpia e independiente del proyecto.
- Fijar el paquete Unity MCP a una revisión completa y reproducible.

## Orden recomendado de mejora

### P0 — Crear una barra visual verificable

1. Producir las hojas VIS-01…19 o, como mínimo inicial, VIS-01…04 y VIS-11…17.
2. Elegir una habitación vertical slice: apertura S1 con criocámara, puerta y Vigía.
3. Fijar cámara, escala, paleta, iluminación, materiales y composición antes de rehacer todos los assets.
4. Aceptar el segmento con capturas comparables bajo luz neutra, luz de juego y cámara real.

### P1 — Rehacer los assets que dominan la pantalla

1. Brazos/manos y grips de las tres armas.
2. Vigía como enemigo base y prueba del pipeline de robot.
3. Criocámara y puerta corrediza para la apertura.
4. Pistola y escopeta por su exposición constante en primera persona.
5. Custodio y Archivista una vez validado el pipeline del Vigía.

Cada fuente debe separar high/low, rig, export y colisión; incluir UV y bake verificables, materiales con desgaste causado, LOD cuando corresponda y renders antes/después. No conviene aumentar polígonos sin mejorar silueta, anatomía, materiales o lectura en cámara.

### P2 — Sustituir placeholders y vestir el búnker

1. Crear al menos un humano focal completo y variantes LOD/pose para jaulas y clínica.
2. Terminar mobiliario modular, señalética, vidrio, trims y decals.
3. Aplicar una biblioteca PBR coherente de concreto, metal pintado, óxido, goma, vidrio, piel, tela y sangre.
4. Rehacer iluminación por sector y añadir profundidad atmosférica sin romper el perfil de rendimiento.
5. Mejorar el exterior con relieve, ruina, siluetas y niebla estratificada.

### P3 — Cerrar movimiento, física y entrega

1. Pasada artística de patrulla, ataques, daño y muerte; añadir giro de cabeza y gesto de huella.
2. Completar reacciones físicas y conflicto puerta/carro.
3. Regenerar prefabs y escenas, ejecutar las suites completas y revisar visualmente la campaña.
4. Crear una nueva build Release desde el commit final, repetir métricas y probar una copia limpia.

## Pipeline de skills para la siguiente iteración

`blender-skill-harmonizer` debe coordinar el trabajo. Para assets con hojas VIS: `reference-analysis-validator` → `orthographic-registration` → `multiview-constraint-solver` → modelado/ajuste → UV y cobertura → comparación multivista → materiales/look → exportación → animación → `animation-quality-gate`. Para la habitación vertical slice: `blender-pro-workflow` coordina bloqueado, cámara, iluminación, geometría, materiales y render. Unity debe validar escala, prefabs, colliders, clips, materiales URP, LOD y rendimiento después de cada exportación.

## Criterio de cierre visual

No volver a declarar Tier A por conteo de tris. Un asset queda conforme cuando su ficha, hoja VIS, fuente Blender organizada, high/low cuando aporte valor, UV/bake, materiales, rig/animación, LOD/collider, prefab y capturas en cámara real coinciden y pasan revisión humana. La primera meta concreta debe ser que la apertura S1 alcance ese estándar antes de extenderlo al mapa completo.
