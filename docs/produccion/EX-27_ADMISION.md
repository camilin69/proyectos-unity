# EX-27 · Admisión y objetos cotidianos

Cuatro fichas y una variante, con fuentes Blender, FBX, atlas PBR y prefabs de una malla/material cada uno.

| Ficha | Entrega | Triángulos | Atlas |
|---|---|---:|---:|
| OBJ-040 | Taza y termo intactos | 1208 | 512 |
| OBJ-040, variante 040B | Taza desportillada, termo intacto | 1208 | 512 |
| OBJ-058 | Atril de admisión | 540 | 1024 |
| OBJ-063 | Pizarra de turnos | 476 | 1024 |
| OBJ-064 | Contenedor clínico | 1168 | 1024 |

La taza tiene pared interior, base cerrada, asa conectada y mancha interior localizada. Se corrigió un giro de anillos en el asa y el cruce de la geometría de la mancha con las caras interiores antes de los bakes finales. Alturas: taza 0.09 m y termo 0.25 m. La variante 040B rebaja físicamente el borde frontal; no se simula la rotura con color. Ambas carecen de collider propio. La versión intacta está apoyada a 1 mm de la superficie de M027; la desportillada queda como prefab reutilizable.

El atril mide 0.6 × 0.4673 × 1.2005 m, con pedestal, carpeta inclinada, clip y control. Su página impresa reproduce un extracto de DOC-06 de DocumentLibrary. Reemplaza Support_DOC-06 en REG-S3. El pickup conserva GUID, identificador y cantidad; su caja queda accesible sobre el papel, y su antigua malla cian se desactiva. La página física del atril permanece después de archivar el documento. El comportamiento actual usa el archivo de documentos existente; clic contextual y lectura con pausa de la ficha siguen pendientes.

La pizarra mide 1.2 × 0.8 m y queda apoyada en el muro de admisión, encontrado mediante raycast a X=186. Tiene anotaciones originales legibles: recepción, revisión y guardia, sustituidas por la prórroga indefinida de EVA. Son parte del atlas, no texto flotante. El contenedor mide 0.4 × 0.3155 × 0.6 m contando cierre; tiene tapa sellada, borde de bolsa opaca, asas y señalización. Se coloca junto al área de drenaje, en (222.5,-8,59).

Validación: coincidencia de topología y ejes Blender/Unity, capturas neutrales y regionales, 81/81 Edit Mode (b995f0f364b14d5e9a9ca7a025d0995c, 1.821 s). La prueba AdmissionSceneTests confirma identidad de DOC-06 y que el primer impacto del rayo de lectura sea su pickup, antes que la carcasa del atril. Evidencias en SourceArt/_evidence/EX-27. No se atribuye nueva ejecución Play Mode a esta entrega.

Build Windows EX27-Admission: Succeeded, 310.08 MB, 21.89 s, cero errores y cuatro advertencias. Registro en evidencia/build_EX27-Admission.json.

Pendientes: desgaste y revisión artística localizada, borrado/polvo de pizarra, respuesta sonora/lectura pausada del atril y recorrido final junto al contenedor. Los modelos están integrados, no declarados Conforme. Continúa el objetivo global.
