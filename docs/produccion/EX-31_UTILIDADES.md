# EX-31 · Megafonía, iluminación e instalaciones

Cinco fichas producen ocho modelos mediante `SourceArt/Scripts/build_utilities_ex31.py`. Cada modelo tiene fuente Blender, FBX, prefab y atlas PBR con BaseColor, Metallic, Roughness y Normal. Las luminarias añaden una máscara de emisión sobre las mismas UV.

| Modelo | Triángulos | Dimensiones Blender XYZ (m) | Atlas |
| --- | ---: | --- | ---: |
| OBJ-065 AltavozMegafonia | 648 | 0.4 × 0.3 × 0.25 | 512 |
| OBJ-066 LuminariaTecnica | 532 | 0.8 × 0.2 × 0.1505 | 512 |
| OBJ-067 LamparaEmergencia | 241 | 0.3 × 0.1506 × 0.12 | 512 |
| OBJ-068 BandejaCables2m | 452 | 2 × 0.5 × 0.282 | 1024 |
| OBJ-068B BandejaCables4m | 572 | 4 × 0.5 × 0.282 | 1024 |
| OBJ-069 Conducto2m | 800 | 2 × 0.74 × 0.79 | 1024 |
| OBJ-069B Conducto4m | 848 | 4 × 0.74 × 0.79 | 1024 |
| OBJ-069C RejillaTerminal | 584 | 0.10 × 0.66 × 0.66 | 1024 |

Todos quedan dentro del presupuesto geométrico de su ficha. Las bandejas tienen cuatro cables, travesaños, bridas y soportes; sus extremos respetan exactamente los módulos de 2 y 4 m. Los conductos son huecos, con bridas y soportes; la rejilla terminal tiene nueve lamas y fondo oscuro. Los atlas de bandejas y conductos todavía son por modelo: no satisfacen aún el requisito de material tiling compartido.

## Integración

UtilityFixturesReview coloca 57 luminarias técnicas: 6 en S1, 19 en S2, 20 en S3 y 12 en S4. Comprueba el techo y los cuatro apoyos antes del montaje. Conserva las luces existentes como hijas, sus colores, intensidades, alcance y ajustes de sombras. Circ_P01-ESC queda pendiente porque no se detectó techo válido. Las luces deshabilitadas y las luminarias del kit S1 ya existente no se sustituyen.

FixtureEmission refleja el color y la intensidad de la luz vinculada sobre la máscara del difusor. Apagar la luz o llevar su intensidad a cero apaga la emisión. No añade luces, audio ni parpadeo. Las luminarias y bandejas no incorporan colliders innecesarios; los conductos usan cajas simples y el altavoz una caja en el soporte.

El altavoz de C1 conserva AnnouncementSpeaker, su vínculo D06, subtítulos y secuencia narrativa. La carcasa anterior se oculta y el nuevo soporte se ajusta al muro. No se añade AudioSource ni un disparador nuevo. Las identidades narrativas se conservan. Las posiciones reales están en `SourceArt/_evidence/EX-31/placements.tsv`.

OBJ-067, OBJ-068/068B y OBJ-069/069B/069C están preparados como prefabs; todavía no se han trazado rutas ni colocado regionalmente. RegionSceneBuilder incluye UtilityFixturesReview. La reaplicación no cambia escenas ya integradas y repara las referencias a luces después de reimportar prefabs.

## Validación

- Capturas de los ocho modelos en Blender y Unity revisadas; hojas `source_sheet.png` y `unity_sheet.png` en EX-31. Capturas regionales `Luminaire_EX31.png` y `Speaker_EX31.png`.
- Siete pruebas específicas verifican máscaras, apagado de emisión, referencias a luces, contacto con techo y conservación del altavoz D06 sin AudioSource adicional.
- Suite **91/91 Edit Mode**, trabajo `71d933dd5598485d93371e6405826991`, 2.2359451 s. XML nativo en `SourceArt/_evidence/EX-31/edit-mode-tests.xml`, ejecución 2026-09-19 20:14:27–20:14:30 UTC.
- No se ejecutó nueva suite Play Mode. La última suite completa sigue siendo la de EX-20; EX-26 añadió una prueba específica.
- Build Windows **EX31-Utilities: Succeeded**, 322.04 MB, 41.09 s, cero errores y 55 advertencias. Registro en `evidencia/build_EX31-Utilities.json`. El build valida las escenas y código integrados; no demuestra inclusión de prefabs aún sin referencias regionales.
- Consola sin errores y escena REG-S1 sin cambios pendientes al terminar.

## Pendientes de aceptación

La captura regional muestra un punto brillante sobre la luminaria debido a la luz puntual existente sin sombras. Falta resolver esa coherencia con el presupuesto de iluminación y revisar con jugador. El altavoz necesita audición de la secuencia completa con D06 cerrada y abierta, filtro, reverberación y subtítulos. La lámpara de emergencia necesita colocación, orientación, rótulo de servicio y acabado. Bandejas y conductos necesitan material tiling compartido, rutas, conexiones y remates; audio, partículas o vibración donde corresponda a la ficha. No se declara ningún modelo Conforme. El objetivo global permanece activo.
