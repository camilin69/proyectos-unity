# EX-46 · Adulto deteriorado

HUM-03 aporta la tercera base adulta. Es más baja y estrecha, con curvatura continua desde pelvis a columna, pérdida localizada de volumen en mejillas y sienes, piel más pálida y vendajes con capas separadas en antebrazo y tobillo. Conserva manos, pies y rostro completos; la deformación no procede de decimado ni ruido aleatorio.

El humano tiene 18 028 triángulos, 30 huesos, dos mallas skinned y dos atlas PBR 1K. Su loop dura siete segundos: respiración de 1.8 mm y una respuesta de dedo de cuatro grados. PreservedSubject le asigna fase 0.32, distinta de HUM-01 y HUM-02.

HUM-03_SoporteLateral es una plataforma baja de 540 triángulos y atlas 512, con colchón sellado, cojín lateral elevado, almohadilla de cabeza, costillas estructurales y patines. La asamblea coloca el cuerpo sobre su lado izquierdo: brazo inferior junto a la cabeza, brazo superior visible y cabeza apoyada. Suma 18 568 triángulos y sustituye el placeholder de M046 en REG-S3, conservando la placa de Lucía Soler.

## Verificación

- 121/121 pruebas Edit Mode: presupuesto, pesos, ejes Blender/Unity, deformación de ropa, orientación lateral y soporte propio.
- Captura neutral de la asamblea y vista regional desde el pasillo revisadas.
- Hoja de contacto de cuatro tiempos sin alertas automáticas; la respiración es sutil a propósito.

La fuente reproducible es `SourceArt/Scripts/build_deteriorated_adult_ex46.py`. Evidencia, mapas, capturas y XML se guardan en `SourceArt/_evidence/EX-46/`.

## Pendiente

La cara y las manos siguen siendo una primera versión estilizada. Conviene acentuar la atrofia en clavículas y articulaciones sin romper la anatomía, crear LOD y revisar el conjunto bajo la linterna real. Falta audio ambiental. Estado Integrado, `acceptance_proven=false`.
