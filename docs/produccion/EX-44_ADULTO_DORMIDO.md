# EX-44 · Adulto dormido

HUM-01 incorpora una fuente original de Blender, FBX, dos atlas PBR 1K (piel y ropa), rig de 30 huesos y respiración de cinco segundos. Tiene 17 484 triángulos y altura de 1.795 m. Es una primera versión estilizada; no se considera terminado artísticamente.

El prefab HUM-01_CamillaDormido combina el humano, la camilla existente y apoyos separados HUM-01_ApoyosCamilla (2272 triángulos, atlas 512). Sustituye el placeholder de M041 en REG-S3, conservando su placa de identidad. RegionSceneBuilder reproduce la integración. Los demás sujetos esperan sus variantes y poses propias.

La respiración desplaza el pecho 2.8 mm y deforma la ropa; cabeza y pies permanecen estables. SleepingSubject aplica una fase inicial sin añadir IA, daño o colisiones al humano. La animación se detiene con la pausa del juego.

Se corrigieron hombros abultados, intersección de pantalón y bata, posición de brazos y un hueco bajo el torso. Los apoyos se midieron contra las mallas reales del colchón. En reposo: cabeza −0.64 mm, torso +5.96 mm y talones +0.06 mm respecto al apoyo; al inspirar, torso +8.20 mm. Son tres muestras anatómicas, no una simulación completa de contacto.

## Verificación

- 117/117 pruebas Edit Mode, incluyendo escala, pesos, correspondencia de vértices Blender/Unity, deformación y apoyos.
- 1/1 prueba Play Mode específica de respiración, fase y pausa. No constituye una repetición de toda la suite de juego.
- Cuatro fotogramas de Unity actualizados y hoja de contacto revisada: silueta estable; el análisis no reporta saltos. No acredita ausencia de parpadeo en todas las condiciones de juego.
- Build Windows EX44-SleepingAdult: 461.28 MB, cero errores y 55 advertencias. Informe en evidencia/build_EX44-SleepingAdult.json.

Fuentes reproducibles: SourceArt/Scripts/build_sleeping_adult_ex44.py y SleepingAdultReview.cs. Evidencia y XML en SourceArt/_evidence/EX-44/.

## Pendiente

Refinar rostro, continuidad de párpados, manos y materiales a distancia cercana; crear LOD; revisar con iluminación final y desde el recorrido del jugador. HUM-02, HUM-03 y la manta OBJ-054 siguen pendientes. Las capturas regionales iniciales preceden a la última corrección de apoyos; la hoja de contacto sí corresponde al montaje corregido. Estado Integrado, acceptance_proven=false.
