# EX-43 · Monitor mural

OBJ-074_MonitorMural: fuente original en `SourceArt/Scripts/build_wall_monitor_ex43.py`. Carcasa, sello de pantalla, marco, tapa trasera, tornillos, raíles separados de montaje, placa mural, rejilla inferior, enchufes y tramo corto de cable protegido.

1288/2000 triángulos. Dimensiones Blender XYZ: 1.20 × 0.107 × 0.70 m. Una malla de carcasa/pantalla, con atlas PBR 1K. La placa posterior termina en Y=0.05 m: el montaje deberá apoyar esa superficie contra un muro real, sin escalar el modelo. Un volumen de colisión simple, sin trigger independiente.

## Pendientes de integración funcional

La pantalla queda apagada hasta disponer de su fuente de datos. Las jaulas actuales se generan con FurnitureBuilder; los sujetos aún son placeholders. No se ha conectado un controlador de estados de jaulas ni vídeo de sujetos. Quedan montaje regional, lectura vinculada a datos guardados, variante decorativa, LOD y acabado localizado. El cable corto termina en la trasera: falta continuar la conexión al muro al instalar.

La existencia de fuente, mapas o prefab no prueba aceptación final. Evidencia geométrica y capturas en `SourceArt/_evidence/EX-43/OBJ-074_MonitorMural/`.

## Verificación de esta entrega

FurnitureReview.Integrate comprobó coincidencia de triángulos, una submalla, presencia de los cuatro mapas y conversión de ejes contra vértices de la fuente. Prefab creado con una caja de colisión; capturas frontal y posterior de Unity revisadas. No se modificó ninguna escena regional ni se añadió comportamiento runtime. No se ejecutaron nuevas suites de pruebas ni build. Estado: prefab validado geométricamente, aceptación funcional y artística pendiente.
