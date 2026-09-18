# ESNEIDER — Protocolo Lázaro · paquete de entrega (91.5)

Versión de producto `0.1.0` · commit de referencia: ver `docs/produccion/evidencia/build_Release.json` · Unity `6000.6.1f1` (URP 17.6) · Blender `5.2.1 LTS`.

## Qué es

Terror en primera persona dentro del búnker NÉMESIS: Esneider despierta 2000 años después de una preservación "temporal" y atraviesa cuatro sectores (S1 Lázaro, S2 mantenimiento, S3 contención, S4 control) conectados por tres corredores, con tres armas (varilla, pistola, escopeta), linterna, Vigías (red de captura), Custodios (rayo) y el jefe EL ARCHIVISTA, checkpoints con snapshot del mundo y escape final al exterior. Diseño íntegro en `docs/ESNEIDER_BUNKER_GDD.md` (106 secciones) y `docs/ESNEIDER_FICHAS_OBJETOS.md`.

## Ejecutar la build

`Builds/Windows/Release/EsneiderProtocoloLazaro.exe` (Windows 10/11 x64, DirectX 11, 1280×720 ventana por defecto; probado en i5-7500 / Intel HD 630 / 24 GB, perfil local 720p/30 con margen).

Argumentos de línea de comandos para QA sin operador: `-autotest -perfroute S1_apertura|S2_nave|S3_jaulasA|S3_clinica|S4_control|S4_boss` (tramos 91.4) y `-autotest -perfsession <minutos>` (sesión de streaming con memoria). Los informes se escriben en `%USERPROFILE%/AppData/LocalLow/DefaultCompany/EsneiderProtocoloLazaro/perf_*.json`.

Las builds no se versionan (`Builds/` está en `.gitignore`); se regeneran desde el editor con `Esneider.EditorTools.PlayerBuilder.BuildWindows(development, label)` o desde el menú de Unity Build Settings (escenas BOOT + REG-*).

## Abrir el proyecto

1. Unity Hub → Add → `EsneiderProtocoloLazaro/` (Unity 6000.6.1f1). Paquetes resueltos desde `Packages/manifest.json` (URP, Input System, AI Navigation, uGUI, Test Framework, MCP for Unity opcional).
2. Escena de arranque: `Assets/_Game/Scenes/BOOT.unity` (carga REG-S1 y vecinas por streaming). Escenas auxiliares: `Combat_Sandbox`, `Bunker_Blockout`, `Art_Showcase`.
3. Regenerar contenido desde datos (idempotente): `BaselineDataCreator` (catálogo 95), `RegionSceneBuilder.Build()` (blockout 68 + mobiliario 76 + patrullas 77 + eventos 93 + NavMesh), `SandboxBuilder.Build()`, `ShowcaseBuilder.Build()`.
4. Pruebas: Test Runner → EditMode (`Esneider.Tests.EditMode`, 23) y PlayMode (`Esneider.Tests.PlayMode`, 30). Resultados versionados en `docs/produccion/evidencia/tests_*.md`.

## Controles (teclado y ratón; mando no soportado)

| Acción | Tecla |
|---|---|
| Moverse / correr / agacharse / saltar | WASD / Shift / Ctrl / Espacio |
| Mirar / atacar o disparar | Ratón / clic izquierdo |
| Recargar / linterna / curar | R / F / Q |
| Cambiar arma | 1 varilla · 2 pistola · 3 escopeta · rueda |
| Interactuar (puertas, pickups, documentos, palancas, paneles) | E |
| Pausa (mapa, documentos, ajustes, controles) | Esc |
| Omitir apertura | E o Espacio |
| Reintentar tras derrota / resultados tras la victoria | Enter |

Ajustes persistentes (fuera del guardado): sensibilidad, invertir Y, FOV 70–100°, tamaño de texto 100–150 %, subtítulos, balanceo, volumen y **asistencia opcional** (telegraphs +25 %, rayos −20 %) que nunca se activa sola.

## Estructura del repositorio

- `EsneiderProtocoloLazaro/` proyecto Unity (`Assets/_Game/{Scripts,Data,Scenes,Prefabs,Art,Audio,Tests}`).
- `SourceArt/` fuentes Blender (`.blend`), scripts `bpy` de fabricación, hojas de evidencia por asset y `Audio/gen_audio.py`.
- `docs/` GDD maestro, fichas, `produccion/` (registro MCP OP-0001…, baseline técnico, matriz de skills, manifiesto de audio, evidencia) y `entrega/` (este paquete: README, licencias, matriz del taller, informe QA, acta).
- `tools/` utilidades de datos (transcripción de tablas del GDD al plano JSON).

## Créditos

Diseño y documento maestro: autor del GDD. Fabricación de assets (Blender por MCP), código Unity, síntesis de audio y pruebas: producción asistida por Claude (Anthropic) bajo el contrato operativo de la sección 94 del GDD, con registro de cada operación en `docs/produccion/REGISTRO_MCP.md`. Voz de megafonía: Microsoft SAPI (Sabina) procesada según 72.3. Motor Unity (Unity Technologies), Blender (Blender Foundation).

## Problemas conocidos

Ver `docs/entrega/QA_REPORT.md` (defectos abiertos y limitaciones) y el acta de cierre `docs/entrega/ACTA_CIERRE.md`.
