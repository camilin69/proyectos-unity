# EX-45 · Adulto con injertos

HUM-02 incorpora una segunda base adulta, de hombros más anchos y proporciones distintas a HUM-01. El brazo biológico izquierdo se elimina por debajo del injerto: la prótesis no cubre una extremidad completa escondida. La transición incluye tejido cicatrizado, manguito de polímero, eslabón estructural, articulación de codo, carcasa de antebrazo, dos raíles, cable de servicio, muñeca y mano mecánica con cuatro dedos y pulgar.

El soporte cervical queda abierto por delante y continúa mediante almohadillas de hombro, pieza esternal y dos bandas que comprimen ligeramente la bata. El modelo humano tiene 18 378 triángulos, 30 huesos, tres mallas skinned y tres atlas: piel y ropa a 1K, injerto a 512. No tiene collider, IA ni salud.

HUM-02_SoporteInclinado aporta una estructura distinta a la camilla de HUM-01: 1228 triángulos, atlas 512, larguero central, raíles, cuatro almohadillas, apoyo de talones, placas de pies y cuna cervical. La asamblea suma 19 606 triángulos, se reclina 12 grados y coloca los pies sobre las placas. Sustituye el placeholder de M042 en REG-S3 mirando al pasillo este y conserva la placa de Tomás Leal.

La animación ambiental dura seis segundos. Desplaza el pecho 2.3 mm, mantiene la cabeza estable y añade un ajuste de 0.65 grados en el antebrazo mecánico, suficiente para superar 1 mm de movimiento visible sin convertirse en una reacción de enemigo. PreservedSubject inicia el loop con fase 0.61 y respeta la pausa global.

## Verificación

- 119/119 pruebas Edit Mode: presupuesto, tres mallas, pesos, ejes Blender/Unity, movimiento del injerto y asamblea inclinada.
- 1/1 prueba Play Mode específica: fase distinta, respiración y congelación con pausa.
- Cuatro muestras temporales de Unity y hoja de contacto sin alertas automáticas; el movimiento deliberadamente sutil no se usa como prueba de acabado artístico.
- Vista regional desde el pasillo confirma orientación, silueta tras barrotes y conservación de la placa.

La fuente reproducible es `SourceArt/Scripts/build_grafted_adult_ex45.py`. Evidencia, mapas, capturas y XML se guardan en `SourceArt/_evidence/EX-45/`.

## Pendiente

El rostro, párpados, mano biológica y acabado de la cicatriz siguen siendo primera versión estilizada. Faltan LOD, audio de articulación/exhalación, el evento narrativo único de ajuste y la revisión final con linterna. La prótesis cuenta como OBJ-055 integrada en este sujeto; si se reutiliza en otro cuerpo deberá extraerse como prefab modular propio. `acceptance_proven=false`.
