# Créditos — Sueño Lúcido

## Equipo
- Dirección, diseño y desarrollo: Camilo Merchán (UPTC, Electiva IV).
- Desarrollo asistido con Claude (Anthropic).

## Modelado y animación propios
- **El soñador** (SN-01): figura de tela blanca sin rostro, modelada, simulada (tela) y riggeada en Blender por el
  equipo. Rig Humanoid de 22 huesos; 9 clips propios (Idle, Walk, Jog, JumpStart, Fall, Land, Fly, Swim, Pickup),
  con las velocidades medidas (Walk 1,27 m/s, Jog 2,07 m/s). Fuente: `SourceArt/TallerFinal/`.
- Escenarios, puertas, árbol, palmeras, escaleras, figuras de luz: construidos por código
  (`Assets/_Project/Editor/Build/`).
- Cielo de estrellas, ruido 3D de las nubes, campanilla del recuerdo y zumbido de la luz: generados por código.

## Música
- **Limousine — «Eccochamber (Moon Woman S.O.S.)»**. Uso exclusivamente académico para la presentación en clase.
  La canción es comercial: **no** se incluye en el repositorio público ni se distribuye con el juego fuera del aula.

## Recursos de terceros (CC0)
| Recurso | Autor / fuente | Licencia | Dónde se usa |
|---|---|---|---|
| Leafy Grass (`leafy_grass`) | Charlotte Baglioni · [Poly Haven](https://polyhaven.com/a/leafy_grass) | CC0 | pasto de la pradera y la colina |
| Coast Sand 01 (`coast_sand_01`) | Rob Tuytel · [Poly Haven](https://polyhaven.com/a/coast_sand_01) | CC0 | arena de la playa |
| Forest Leaves 02 (`forest_leaves_02`) | Rob Tuytel · [Poly Haven](https://polyhaven.com/a/forest_leaves_02) | CC0 | suelo del bosque de palmeras |
| Long White Tiles (`long_white_tiles`) | Jenelle van Heerden, Sergej Majboroda · [Poly Haven](https://polyhaven.com/a/long_white_tiles) | CC0 | azulejo de la piscina y del cuarto |
| Interior Tiles (`interior_tiles`) | Charlotte Baglioni · [Poly Haven](https://polyhaven.com/a/interior_tiles) | CC0 | piso del cuarto |
| Velour Velvet (`velour_velvet`) | colormass, Rico Cilliers · [Poly Haven](https://polyhaven.com/a/velour_velvet) | CC0 | moqueta de la escalera |
| Rough Linen (`rough_linen`) | colormass, Rico Cilliers · [Poly Haven](https://polyhaven.com/a/rough_linen) | CC0 | tela del sonador |
| Cotton Jersey (`cotton_jersey`) | colormass, Rico Cilliers · [Poly Haven](https://polyhaven.com/a/cotton_jersey) | CC0 | cobija y cama |
| Bark Willow (`bark_willow`) | Dario Barresi, Dimitrios Savva · [Poly Haven](https://polyhaven.com/a/bark_willow) | CC0 | tronco del arbol monumental |
| Palm Bark (`palm_bark`) | Charlotte Baglioni · [Poly Haven](https://polyhaven.com/a/palm_bark) | CC0 | troncos de palmera |
| White Planks Clean (`white_planks_clean`) | Rob Tuytel · [Poly Haven](https://polyhaven.com/a/white_planks_clean) | CC0 | puertas |
| Marble 01 (`marble_01`) | Rob Tuytel · [Poly Haven](https://polyhaven.com/a/marble_01) | CC0 | estatuas y base de piedra |

Los pasos se sintetizan por código (`Audio/ProceduralSteps`) hasta reemplazarlos por grabaciones aprobadas.

## Software
Unity 6000.6 (HDRP 17.6, Cinemachine 3.1, Timeline, Input System), Blender 5.2, Python (NumPy, SciPy, Pillow), ffmpeg.
