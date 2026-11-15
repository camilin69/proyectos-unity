# EX-25 · Columnas de servicios y montaje de lámparas

OBJ-076 ColumnaServicios: fuente Blender, FBX y atlas PBR 1024; 2124 triángulos, un submesh, sección máxima 1 × 1 m y altura 5 m. Núcleo estructural de 0.84 m, base y capitel, canales protegidos, dos registros con cierres y placas, protección inferior y placa de reparto de carga para la lámpara. Cuatro cajas de colisión y obstáculo NavMesh con carving. Superficie principal SUR-CON.

Se colocan dos columnas junto a las mesas de procedimientos. M056 usa el extremo negativo X; M057 usa el positivo X con giro de 180 grados porque la primera alternativa interceptaba Support_A08 y Pickup_A08. Esos objetos no se movieron. Los volúmenes candidatos definitivos estaban libres de sólidos y pickups antes de colocar, y un rayo superior confirmó techo a 5 m en ambas posiciones.

Las lámparas OBJ-048 se instancian con desplazamiento local (0.461, 0, 0), de modo que su placa posterior toca la placa de reparto de la columna. El centro del cabezal cae sobre la mesa. Un rayo desde cada luz hacia abajo impacta el collider de su propia mesa a altura 0.9 m. M056 tiene una luz dinámica encendida; M057 queda apagada. No hay movimiento de brazos ni daño ambiental añadido.

Validación: conversión de ejes y topología Blender/Unity, dimensiones y contacto de suelo; capturas de ambos montajes; 74/74 Edit Mode, job 32f025c3b3454542a68c2b71d739d24c, 1.726 s. Repetir ClinicalColumnReview.ApplyExisting no modifica ni duplica el montaje. RegionSceneBuilder incorpora el mismo paso. Las capturas y fuente de evidencia están en SourceArt/_evidence/EX-25.

Build Windows EX25-Columns: Succeeded, 295.65 MB, 20.97 s, cero errores y una advertencia. Registro en evidencia/build_EX25-Columns.json.

Pendientes: variante de altura si otras salas la requieren; revisión de densidad y paso a tiling/trim según presupuesto GDD; humedad localizada en base y desgaste de registros; superficie diferenciada para impactos de tapas metálicas; recorrido de jugador y enemigos y prueba de proyectiles/jefe en escena final. El alcance de luz deberá calibrarse con sujetos y brazo clínico. No se declara Conforme ni se atribuye una nueva ejecución Play Mode.
