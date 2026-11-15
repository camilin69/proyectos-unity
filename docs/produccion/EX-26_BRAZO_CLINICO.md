# EX-26 · Brazo clínico

OBJ-050 BrazoClinico: fuente Blender, FBX, atlas PBR 1024, tres mallas rígidas, un material compartido y 1380 triángulos frente a presupuesto 5k. Base mural, cojinete de giro, brazo superior, motor/codo, antebrazo, cableado y herramienta ficticia con puntas redondeadas. Radio horizontal de alcance aproximado 1.33 m desde el pivote del hombro. Pivotes originales verificados después de la conversión de ejes.

ClinicalArmMotion reproduce un ciclo autorado de 20 segundos: 14 en reposo y seis de ida/vuelta con seno al cuadrado, hasta 6 grados de giro de hombro y 4 de elevación de codo. Unity reproduce el movimiento; el FBX contiene la geometría articulada sin clip de animación. El prefab está desacoplado de la jerarquía del modelo para conservar la nueva relación padre/hijo. Una primera captura descubrió que el modelo conectado descartaba esa relación; se corrigió y la prueba ahora exige que los vértices importados se muevan, no solo los pivotes vacíos.

La base tiene la única colisión. No hay callbacks de daño ni collider en la herramienta. Audio mono propio SND-ClinicalServo.wav, sintetizado con armónicos de 96 Hz, a volumen local bajo y bus ambiente. Solo suena al moverse; la pausa detiene movimiento y reproducción, y el reposo detiene el servo. Requiere escucha en mezcla final.

Dos instancias fijadas a las columnas de M056/M057, desplazamiento local X=0.45 m, placa apoyada en concreto. Solo M056 anima; M057 permanece en reposo. La herramienta trabaja debajo de la lámpara. En 121 muestras del ciclo se midieron 166012 posiciones de vértices móviles: envolvente vertical de 1.317621 a 1.845 m, con mesa a 0.9 m y lámpara desde 1.9615 m. Esta medición acredita separación vertical de esos equipos, no certifica futuros sujetos ausentes.

Control visual: contact sheet de seis poses con encuadre fijo, sin cambios de textura y retorno al reposo; captura de M056 en clínica. Evidencias en SourceArt/_evidence/EX-26. 75/75 Edit Mode (51d932bd66e44cfca925c136fafa2dc2, 1.742 s) y 1/1 Play Mode específica de pausa/sonido/retorno (1ec571fd424f469d9854c77a4c973984, 0.336 s); XML guardado. No se presenta esa prueba dirigida como nueva ejecución de toda la suite Play Mode.

Build Windows EX26-ClinicalArm: Succeeded, 299.06 MB, 35.65 s, cero errores y 55 advertencias. Registro en evidencia/build_EX26-ClinicalArm.json.

Pendientes: contacto y recorrido con sujetos/mantas finales, desgaste localizado, escucha en mezcla y revisión artística. Integrado, no Conforme. El objetivo completo continúa activo.
