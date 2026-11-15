# EX-32 · Cámara de vigilancia y variante dañada

OBJ-061 tiene dos variantes originales generadas por `SourceArt/Scripts/build_surveillance_ex32.py`: CamaraVigilancia y CamaraVigilanciaDanada. Ambas incluyen placa mural con cuatro anclajes, brazo de carga, cojinete, carcasa hueca plegada, visera, óptica y cable. La dañada pierde la tapa trasera, expone placa y componentes, conserva fragmentos de lente y presenta cable cortado, visera desplazada y cabezal caído.

| Variante | Triángulos | Dimensiones Blender XYZ (m) | Mallas | Atlas |
| --- | ---: | --- | ---: | --- |
| OBJ-061 | 1540 | 0.170 × 0.307 × 0.200 | 2 | 512, un set |
| OBJ-061B | 1382 | 0.203 × 0.331 × 0.212 | 2 | 512, un set |

Ambas respetan el presupuesto de 2000 triángulos. Las dimensiones incluyen accesorios y, en la variante dañada, el cabezal inclinado. El plano trasero del soporte está en Y=0.15 m de Blender. Los mapas BaseColor, Roughness, Metallic y Normal se empaquetan en la fuente y se exportan a Unity. Se reduce el desgaste genérico por curvatura que desaturaba superficies completas de estas piezas pequeñas; el daño principal tiene geometría propia.

## Contrato de importación

Montura y cabezal son mallas independientes. El pivote del cabezal está en (0,0.055,0.09) en Blender y (0,0.09,0.055) en Unity. SurveillanceCameraReview valida las coordenadas exportadas, desempaqueta el prefab importado y conserva el cabezal bajo SwivelPivot. El error medido de conversión de ejes es cero para ambas variantes. Dos renderers comparten el mismo material y atlas por variante.

No hay collider, AudioSource, percepción ni comportamiento automático. El cabezal está preparado para el giro de unidades activas que se definan regionalmente. La variante dañada es estática visualmente; el daño se incorpora a sus vértices manteniendo el origen nominal del pivote. No hay clips FBX ni animación validada en esta entrega.

## Evidencia

Fuentes en `SourceArt/Blender`, FBX y texturas en `Assets/_Game/Art`, prefabs en `Assets/_Game/Prefabs/Environment`. La carpeta `SourceArt/_evidence/EX-32` contiene informes geométricos, coordenadas, conversión de ejes, recibos de bake e importación, renders de Blender y capturas Unity. La vista trasera de la variante dañada permite inspeccionar la electrónica y el cable cortado.

Validación directa en Unity tras recargar los prefabs: jerarquía persistente, pivote, dos mallas, material compartido, mapas 512 y ausencia de colliders/audio/comportamientos. Resultado en `prefab_validation.txt`. Compilación sin errores y REG-S1 sin cambios pendientes. No se ejecuta nueva suite completa ni build: estos prefabs todavía no tienen montaje regional. Las pruebas 91/91 y el build de EX-31 corresponden a aquella entrega.

## Pendientes

Estado **Prefab validado**, aceptación artística y funcional no probada. Falta seleccionar posiciones y orientaciones compatibles con los puntos ciegos, comprobar la ausencia de observación del sótano antes de la detección narrativa, autorar giro lento y servo solo para unidades activas, validar el recorrido y refinar suciedad localizada. El cabezal separado no demuestra por sí solo que una animación o el cable de una cámara giratoria funcionen correctamente. Objetivo global activo.
