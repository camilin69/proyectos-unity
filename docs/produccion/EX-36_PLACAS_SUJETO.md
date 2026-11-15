# EX-36 · Placas de sujeto OBJ-062

Cinco variantes de la placa de 20 × 10 cm, con 316 triángulos cada una (presupuesto 500), un mesh y un atlas PBR 1024. La placa tiene chapa, cuatro tornillos, dos apoyos posteriores unidos mediante cuatro espárragos y una etiqueta física de EVA superpuesta sobre parte del nombre original. No tiene collider ni sonido dedicado.

## Registro narrativo

`Assets/_Game/Data/LevelPlan/subject_plates_ex36.json` conserva el contrato entre placa, jaula, nombre, serial y año de ingreso. DOC-08 establece la Serie 81, pero no identifica a sus integrantes. Estos cinco nombres y fechas son contenido original añadido en EX-36; no se presentan como texto preexistente del GDD. Los futuros modelos humanos deben respetar esta asociación.

| Fuente | Jaula | Nombre anterior | Serial EVA | Ingreso |
| --- | --- | --- | --- | --- |
| OBJ-062 | M041 | Inés Rivas | 81-041 | 4042 |
| OBJ-062B | M042 | Tomás Leal | 81-042 | 4043 |
| OBJ-062C | M046 | Lucía Soler | 81-046 | 4044 |
| OBJ-062D | M047 | Raúl Mena | 81-047 | 4045 |
| OBJ-062E | M048 | Ana Vidal | 81-048 | 4046 |

M040/M043/M045 son jaulas de mantenimiento sin humano en su ruta navegable y no reciben una identidad personal. No se da a entender que estas personas hayan vivido 2000 años: los ingresos pertenecen a generaciones recientes, según la distinción narrativa del GDD.

## Producción

Scripts `prepare_subject_plates_ex36.py` y `build_subject_plates_ex36.py`. Las dos zonas impresas tienen islas UV propias; herrajes y reverso ocupan otra región del atlas. Las variantes comparten topología, UV y acabados, por lo que reutilizan los mapas Roughness, Metallic y Normal de la primera; cada BaseColor se hornea con su texto original. El desgaste de esquinas es localizado y no degrada las fechas.

## Integración y validación

SubjectPlateReview coloca cada placa sobre un barrote vertical del lado de la jaula que da al pasillo central. Borde inferior a 1.45 m del suelo, apoyos traseros a 0.5 mm de la cara del barrote. Se conserva la escala original. RegionSceneBuilder incorpora el montaje y un contenedor de escena protege la colocación frente a cambios de IDs del FBX.

Suite **105/105 Edit Mode**, trabajo `db2ec8a2d73e460a8a1ecb1f5a94d231`, 3.6390724 s. La prueba nueva verifica cinco seriales distintos, presencia, altura y giro, 316 triángulos, atlas 1K, ausencia de collider/audio y dos rayos por placa que alcanzan el barrote asociado. XML nativo en EX-36. Validación de fuentes: UV idénticas e imágenes originales empaquetadas en las cinco fuentes; importación con error de coordenadas cero. Capturas de los cinco prefabs y montajes regionales. No se ejecutó nueva suite Play Mode porque no se añadió comportamiento runtime.

Build Windows **EX36-SubjectPlates: Succeeded**, 368.41 MB, 21.29 s, cero errores y una advertencia. Registro en `evidencia/build_EX36-SubjectPlates.json`.

## Pendientes

Los sujetos humanos todavía son representaciones provisionales. La placa identifica la composición prevista, pero no prueba la finalización del humano ni de su expediente completo. Quedan lectura durante el recorrido, iluminación definitiva y revisión de montaje cuando las jaulas reciban su arte final. No se declara aceptación artística global.
