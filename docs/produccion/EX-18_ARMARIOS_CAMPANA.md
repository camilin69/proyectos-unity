# EX-18 · Armarios en campaña

Se sustituyeron los soportes provisionales de la pistola y la escopeta, el bloque de taquillas M006 y el placeholder de CP-06 por los cuatro modelos articulados de EX-17. Hay seis instancias en REG-S1/S2/S3/S4. Cada una tiene un identificador persistente propio y puertas excluidas del marcado estático.

La pistola descansa sobre la cuna derecha y la escopeta se coloca vertical sobre el apoyo izquierdo. Se conservaron las entidades PICK-W02/PICK-W03, sus GUID y cantidades 20/10. Sus triggers ajustados quedan dentro del armario cerrado; abrir las hojas permite apuntar al pickup original. Los soportes provisionales desaparecen, sin crear armas adicionales.

CabinetPlacement.Apply queda conectado a RegionSceneBuilder después del vestido de las salas. ApplyExisting actualiza escenas aditivamente y rechaza escenas con cambios sin guardar. Una segunda ejecución devuelve cero cambios y conserva REG-S1 limpia. Los cuerpos incorporan NavMeshObstacle con carving; falta una observación de navegación de enemigos en Play Mode para validar el recorrido junto a las hojas abiertas.

CP-06 conserva las garantías de CheckpointService al confirmar el checkpoint. Abrir o cerrar el gabinete solo modifica su estado de puerta. Los contenedores interiores todavía forman parte de la malla del cuerpo y no representan visualmente el consumo del stock; esa separación y conexión siguen pendientes.

## Evidencia

- 58/58 Edit Mode, 1.58 s, job e2f2fc4233984b28bce015b41a1f7db6. Los cuatro casos nuevos cargan escenas reales y comprueban identidades, cantidades, apertura con el componente real y raycast cerrado/abierto a las armas. SourceArt/_evidence/EX-18/edit-mode-tests.json.
- Barrido de 61 posiciones por puerta, sin penetraciones superiores a 2 mm contra las capas físicas empleadas por HingedCabinet. Informe placements-audit.txt. La primera auditoría incluía volúmenes de región en capas ajenas a la interacción; se corrigió para usar la misma máscara del componente.
- Seis capturas abiertas de las salas en SourceArt/_evidence/EX-18; revisadas las vistas del armario central de preparación, pistola, escopeta y suministros. La iluminación y varios elementos de entorno de S2/S3/S4 aún son provisionales.
- No hay cambios nuevos en la captura del Vigía. La última validación completa de juego de ese comportamiento permanece en EX-17 (38/38); no se atribuye esa ejecución a los cambios posteriores de escena.
- Build Windows EX18-CampaignCabinets: Succeeded, 255.95 MB, 33.44 s, cero errores y seis advertencias (RuntimePipelineConfig ausente y cinco reenvíos MCP suprimidos). Job build-4beb5df69b, informe docs/produccion/evidencia/build_EX18-CampaignCabinets.json. Esta build sí incluye las instancias regionales de los cuatro modelos.

Faltan sonidos de bisagra/cierre, stock visual de CP-06, rotulación/desgaste final y aceptación artística. Las fichas pasan a Integrado, con acceptance_proven=false. El inventario completo sigue conteniendo 101 entradas; esta entrega no completa el objetivo global.
