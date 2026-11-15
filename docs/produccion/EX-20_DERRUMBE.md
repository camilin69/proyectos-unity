# EX-20 · Derrumbe y extracción de varilla

OBJ-012_EscombrosConcreto tiene fuente Blender original, 6252 triángulos, tres mallas y un atlas PBR 1024 compartido. Los volúmenes se construyeron como fragmentos convexos cerrados, con superficies exteriores envejecidas y caras de fractura diferenciadas. El conjunto incluye masa apilada, armaduras curvas con nervios y dos piedras pequeñas independientes. La primera versión rectangular se sustituyó por fracturas irregulares antes del bake final.

M013 en REG-S1/P02 sustituye su bloque provisional por el prefab a escala real, con origen (6,-18,6). Los fragmentos principales usan cajas compuestas; las piedras pequeñas son decorativas y no bloquean la cápsula. RubbleReview.Apply conserva el montaje al regenerar la región. PICK-W01 se trasladó desde su soporte provisional al frente del derrumbe: (7.18,-17.47,7.24), dentro de la misma sala. Conserva GUID 9d9e3673-15fd-af20-82ce-c8971ea45031 y cantidad 1. El raycast de aproximación comprobado alcanza Pickup_PICK-W01.

RubbleExtraction escucha el evento persistente de la varilla. Primero desliza las dos piedras fuera del fragmento de apoyo y después las deja caer, con retraso entre ambas. Emite dos impactos mediante el banco existente SND-PROP-Impact y ruido lógico independiente; no vuelve a ejecutarse por callbacks repetidos. La pausa detiene el avance. Al restaurar o cargar la región, el estado del pickup determina la posición inicial o final sin reproducir sonidos.

## Evidencia y límites

64/64 Edit Mode en 1.62 s, job 9ac66b34a7b748b3b625f8471c8d2210. Incluye tres pruebas nuevas de evento, pausa, repetición, hidratación y evento ajeno. El primer ensayo detectó falta de enlace durante hidratación directa y un residuo de interpolación; se corrigieron y la suite completa pasó. El ensayo fallido no se presenta como validación.

La importación coincide con la fuente en topología, número de mallas y muestras de coordenadas. Los apoyos de las piedras se calcularon mediante raycast sobre la superficie de la fuente. Evidencias bajo SourceArt/_evidence/EX-20: geometry.json, bake.json, source_coordinates.json, axis_conversion.json, unity_import.json, previews, placement.txt y edit-mode-tests.json. El diagnóstico de albedo analiza 43 atlas sin señalar el defecto de metal negro.

39/39 Play Mode, 152.54 s, del 19-09-2026 12:05:11Z a 12:07:44Z. Incluye la prueba PickingUpCrowbarAnimatesPrefabOnceAndRespectsPause con prefab e inventario reales, pausa y dos impactos sin repetición; también conserva las regresiones del escape con F. El job MCP 3352b42ddbe04f97a08678cca0b460a7 perdió callbacks y declaró fallo de inicialización, aunque Unity ejecutó la suite. Se esperó a que el runner nativo terminara y se verificaron fecha, recuento y caso nuevo en su TestResults.xml. La evidencia autoritativa se conserva como play-mode-tests.xml y play-mode-summary.json; no se confunde el estado del transporte con el resultado de las pruebas.

Build Windows EX20-Rubble: Succeeded, 263.16 MB, 37.31 s, cero errores y 60 advertencias. Job build-7fac2349bc; informe docs/produccion/evidencia/build_EX20-Rubble.json. Incluye la viga de EX-19 y el derrumbe con extracción de EX-20.

Pendientes de acabado: polvo breve al caer, contactos y variedad fina de fractura, causa visible del derrumbe en muro/techo y relación con M014, ajuste artístico de concreto/armadura con iluminación final, y revisión del recorrido completo tras trasladar la varilla. Estado Integrado, acceptance_proven=false. No se considera terminada la sala ni el objetivo de todos los modelos.
