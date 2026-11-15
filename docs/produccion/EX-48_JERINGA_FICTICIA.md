# EX-48 · OBJ-056 Jeringa ficticia

OBJ-056 reutiliza el activo `PRP-Syringe` ya existente y cierra la diferencia entre el prop y su ficha de producción.

## Entrega

- Fuente Blender: `SourceArt/Blender/PRP-Syringe.blend`.
- Generador reproducible: `SourceArt/Scripts/build_arms_weapons.py` con `WHICH="syringe"`.
- Export: `Assets/_Game/Art/Models/PRP-Syringe.fbx`.
- Prefab: `Assets/_Game/Prefabs/Weapons/PRP-Syringe.prefab`.
- Geometría: 988 triángulos, 12 piezas y 12 submallas.
- Medida importada: `0.032 × 0.026 × 0.150 m`; la longitud anterior de 0.181 m se corrigió al objetivo de 0.15 m.
- Un atlas PBR de 512 px: BaseColor, Normal, Metallic y Roughness, más el MetallicSmoothness empaquetado por Unity.
- Piezas funcionales separadas: cuerpo, líquido, tapón, vástago, nervio, apoyo de pulgar, aleta, luer, aguja, tapa y estrías.

## Integración de uso

`ViewmodelController` instancia la jeringa en la mano izquierda sólo durante una transacción `Heal` de tipo `Syringe`, oculta temporalmente el arma equipada y reproduce `Arms_Syringe`. La tapa se retira al inicio. Tapón, vástago, nervio y apoyo avanzan hasta el fondo exactamente en el commit configurado por `PlayerDefinition.syringeCommit` (1.1 s de una acción de 1.6 s). El mismo inicio reproduce el banco 2D `SND-SYRINGE-Use`.

El gameplay conserva sus guardas: no cura ni consume a vida completa, cancelar antes del commit conserva la unidad, y al commit consume una jeringa y aplica 45 HP. Los doce pickups H01-H12 usan el prefab mediante `HeroDressing`; el viewmodel queda cableado en `Player_Esneider.prefab` y en cualquier reconstrucción posterior mediante `ShowcaseBuilder.AttachViewmodel`.

## Evidencia y validación

- Blender: `SourceArt/_evidence/EX-48/PRP-Syringe/` contiene vistas ortográficas/isométrica y el informe geométrico.
- Unity: `unity_import.json` confirma 988 triángulos, 12 submallas y tamaño `0.03 × 0.03 × 0.15 m`.
- EditMode: `SyringeModelTests.Obj056HasRequiredPartsExactLengthAndPlayerWiring`, 1/1 pasada.
- PlayMode: `SyringeViewmodelPlayTests.HealingShowsPropMovesPlungerAtCommitAndRestoresWeapon`, 1/1 pasada; valida aparición, avance previo al commit, consumo/curación en el commit y retirada al terminar.
- La regresión económica y transaccional sigue cubierta por `SandboxPlayTests.QA08_HealAtFullDoesNotConsume_AndCancelBeforeCommitKeepsUnit`.

La ficha queda en `Integrado` con `acceptance_proven=false`. Falta la aprobación visual final del contacto con ambas manos en la cámara real, reemplazar parte de los soportes genéricos H01-H12 por gabinetes o stock clínico y, si lo exige la dirección de audio, separar tapa y roce en eventos distintos.
