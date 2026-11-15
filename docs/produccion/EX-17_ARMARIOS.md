# EX-17 · Armarios articulados

Cuatro fuentes Blender originales, con cuerpo y dos hojas separados, interiores modelados, bisagras, manijas, cierre, estantes y un atlas PBR 1024 compartido. Las puertas tienen espesor y pivotes propios; no se unieron al cuerpo para simular después la apertura.

| Ficha | Modelo | Triángulos | Mallas |
|---|---|---:|---:|
| OBJ-007 | Armario de preparación | 5368 | 3 |
| OBJ-024 | Locker de seguridad | 5128 | 3 |
| OBJ-025 | Armario de escopeta | 6028 | 3 |
| OBJ-026 | Gabinete de suministros | 6596 | 3 |

Dimensiones principales según ficha: 1 × 0.5 × 1.9; 1 × 0.55 × 1.9; 1.2 × 0.55 × 1.9; 1 × 0.5 × 1.8 m respectivamente. Manijas y bisagras sobresalen de esas cajas nominales. Ropa doblada/archivo, cunas de arma, soportes fijados al fondo y contenedores distinguen los interiores. Las armas y reservas jugables permanecen entidades independientes; no se fabricaron pickups duplicados.

## Exportación y comprobación

build_cabinets_ex17.py conserva escenas anteriores, fabrica grupos separados, despliega un atlas común y exporta FBX con tres submeshes que comparten material. Fuentes y mapas quedan empaquetados. Los colliders del cuerpo no llenan el hueco del armario; cada hoja lleva su caja móvil.

CabinetReview.Integrate compara triángulos, materiales, muestras de vértices y posición de bisagras. Los cuatro imports coinciden con las fuentes. Se revisaron capturas abiertas y cerradas en Unity. El bake inicial de dos assets en una llamada agotó la espera del servidor, pero los recibos y archivos confirmaron que terminó; no se repitió. Los siguientes se ejecutaron individualmente por Blender MCP.

HingedCabinet anima las hojas por pivote, comprueba obstáculos por pasos y confirma el estado al completar el movimiento. PersistentEntity reconoce el armario como entidad Door para hidratar su estado sin ruido ni animación. Los prefabs dejan los identificadores vacíos hasta asignar instancias únicas durante la colocación; no comparten un GUID de plantilla.

## Alcance pendiente

Validación final: **54/54 Edit Mode**, job fe47ad0913924e4aa9a38bbeb42c0bbe. Incluye cuatro casos de hojas que bloquean/cambian a paso libre y tres de movimiento, pausa, obstrucción/reintento e hidratación/publicación de estado. Evidencia: SourceArt/_evidence/EX-17/edit-mode-tests.json. El primer intento ec81c71ca5134850ad417037b0463ae5 terminó sin iniciar pruebas y no cuenta como validación.

Build EX17-Cabinets: Succeeded, 238 MB, 32.21 s, cero errores y 55 advertencias. La consola incluye APIs de búsqueda obsoletas CS0618 en sistemas existentes y RuntimePipelineConfig ausente de com.unity.pipeline. Informe: docs/produccion/evidencia/build_EX17-Cabinets.json. La build valida el código actualizado; los cuatro modelos todavía son prefabs del proyecto sin instancias regionales, por lo que no se presentan como contenido nuevo visible en esa build.

Esta entrega prepara prefabs articulados. **Aún no están colocados en la campaña**. Faltan asignar identificadores de instancia, sustituir soportes de PICK-W02/PICK-W03, ajustar armas a sus cunas, comprobar reservas y acceso en salas, conectar stock visual y transacción de CP-06, añadir sonidos de bisagra/latch y cerrar desgaste y rotulación. No se considera Conforme ninguna de estas fichas.

PICK-W02 se encuentra en P04 (6,8), altura 1 m; PICK-W03 en P05 (54,5), altura 1.1 m. Conservar identidades, cantidades y semántica existentes al trasladar sus visuales. El gabinete final debe respetar la garantía idempotente de CheckpointService, no conceder recursos por cada apertura.

La captura del robot pequeño conserva su comportamiento de escape con F y daño gradual. La suite completa de juego pasa 38/38 en 152.57 s, job 6ce14265e3624b97b0ad7452a7ef824c. Evidencia en SourceArt/_evidence/EX-17/play-mode-tests.json. La suite de juego cubre regresiones existentes; el contrato específico de los armarios se comprueba en las pruebas nuevas de edición.

Reproducción: build(id), render(id, opened), finish(id) en Blender MCP; CabinetReview.Integrate/Capture en Unity MCP. Skills de modelado, materiales, exportación y revisión visual aplicadas a los assets; patrones de interacción, física, persistencia y pruebas Unity aplicados al componente.

El objetivo completo conserva las 101 entradas del inventario y permanece activo.
