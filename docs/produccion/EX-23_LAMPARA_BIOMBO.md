# EX-23 · Lámpara clínica y biombo

Dos modelos originales con fuentes Blender, FBX, atlas PBR 1024 y prefabs. La importación valida triángulos, un submesh y conversión de coordenadas contra muestras de la fuente. Las capturas de Unity se encuentran en SourceArt/_evidence/EX-23, incluida la cara inferior de la lámpara.

| Modelo | Triángulos | Medidas |
|---|---:|---|
| OBJ-048 LamparaClinica | 1912 | Cabezal de 0.6 m; envolvente Unity 1.55 × 0.6835 × 0.6 m |
| OBJ-053 Biombo | 1480 | Unity 1.502 × 1.8 × 0.498 m |

La lámpara tiene placa de anclaje mural, pernos, articulaciones, cable protegido, siete lentes con marcos y grip central. Su origen corresponde al piso bajo el anclaje; la geometría queda elevada, de 1.9615 a 2.645 m. Solo la placa tiene colisión. El spot opcional está situado bajo el cabezal en (1.22, 2.085, 0), apuntando hacia abajo, desactivado por defecto para que la colocación decida qué luces son dinámicas. Su estado autorado es estático.

El biombo incorpora marco, cuatro ruedas, pies transversales y tela plegada con grosor de 2.5 mm y dobladillos. Tiene tres cajas de colisión: panel y dos pies; no se bloquea con una caja todo el hueco inferior. La tela opaca conserva cobertura por ambas caras.

Se redujo la densidad de cilindros y pliegues antes de hornear los atlas. Ambos quedan dentro de los presupuestos de 3k y 2k triángulos. Las 72 pruebas Edit Mode pasaron (job 2e4fba5ec9104eb89f2caff67ed10a07, 1.642 s), incluyendo dimensiones y contacto con suelo del biombo, y origen/orientación del cono de la lámpara. No hay nueva build ni nuevo resultado Play Mode en esta entrega; la build previa es EX22-Devices.

Pendientes: montaje de lámpara junto a la futura mesa OBJ-044, soporte de peso y cono sobre procedimiento; composición de la mampara M058 de 5 m sin estirar los biombos, con recorrido y cobertura verificados; desgaste localizado y aprobación artística. Son prefabs validados, sin instancias regionales todavía, no Conforme. El objetivo completo permanece activo.
