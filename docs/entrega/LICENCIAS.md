# Manifiesto de licencias y procedencia (91.5 / 100)

Ningún asset se descargó de tiendas ni bibliotecas externas: no se usaron Poly Haven, Sketchfab, Poly Pizza ni generadores 3D. Todo el contenido 3D, texturas, animación, audio y código es original del proyecto salvo lo indicado.

| Contenido | Origen | Licencia / condición |
|---|---|---|
| 16 assets hero (BOT-01/02/03, CHR-01, WPN-01…04, PRP-Syringe/Ration, OBJ-001/041/070/059/043/029) | Modelados por procedimiento en Blender 5.2 con `SourceArt/Scripts/*.py` vía MCP; UV, horneado PBR, rig rígido y clips propios | Original del proyecto. Fuentes `.blend` y FBX incluidos |
| Kit de mobiliario y blockout (cajas, barrotes, placeholders de sujetos) | Generado por `RegionSceneBuilder`/`FurnitureBuilder` desde `bunker_plan.json` | Original; declarado como no final (Revisar) |
| Texturas `Assets/_Game/Art/Textures/*.png` | Horneadas desde materiales procedurales de Blender | Original |
| 91 efectos de sonido y ambientes `Assets/_Game/Audio/**` | Sintetizados con numpy/scipy (`SourceArt/Audio/gen_audio.py`); ficha por archivo en `docs/produccion/AUDIO_MANIFEST.json` | Original |
| Voz de megafonía `SND-PA-Detection` | Texto a voz Microsoft SAPI 5 (voz "Sabina", Windows 10) grabado localmente y procesado (72.3) | Uso de la voz del sistema; **verificar antes de una distribución comercial** que las condiciones de Microsoft permiten redistribuir audio generado (uso académico/no comercial previsto) |
| Textos narrativos DOC-01…12, nombres y guion | Ficción original del GDD (57) | Original |
| Fuente de interfaz | `LegacyRuntime.ttf` integrada en Unity | Unity Companion License |
| Unity 6000.6.1f1, URP, Input System, AI Navigation, uGUI, Test Framework | Unity Technologies | Unity Companion License / Unity Terms |
| MCP for Unity (`com.coplaydev.unity-mcp`) | Coplay Dev (herramienta de desarrollo; no forma parte de la build) | Licencia del paquete (MIT según repositorio; no redistribuida en la build) |
| Blender 5.2.1 LTS y addon Blender MCP | Blender Foundation / addon de terceros (herramienta; no distribuida) | GPL (herramienta), no afecta a los assets producidos |

Autoría: producción asistida por Claude (Anthropic) siguiendo el GDD del autor; la autoría creativa y la responsabilidad de la entrega son del autor del proyecto. No se afirma propiedad sobre marcas, voces ni software de terceros.
