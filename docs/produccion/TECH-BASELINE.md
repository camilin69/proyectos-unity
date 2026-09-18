# TECH-BASELINE — computador destino (sección 105)

Fecha de inspección: 2026-09-17 · Etapa EX-00 · Revisión 1.

## Entorno

| Campo | Dato verificado |
|---|---|
| SO | Windows 10 Pro 10.0.19045 x64 |
| Raíz del repositorio | `C:\Users\HP\Documents\GitHub\proyectos-unity` (git, rama `main`, remoto GitHub `camilin69/proyectos-unity`) |
| Proyecto Unity | `EsneiderProtocoloLazaro/` (dentro del repo) |
| Fuentes Blender | `SourceArt/Blender/` (fuentes `.blend`), `SourceArt/Textures/`, `SourceArt/_probe/` (ensayos), `SourceArt/_evidence/` (capturas) |
| Exports de producción | `EsneiderProtocoloLazaro/Assets/_Game/Art/Models/` |
| Git LFS | git-lfs 3.4.0 disponible; adopción pendiente de decisión (98.1) — no activado todavía |

## Hardware

| Campo | Dato |
|---|---|
| CPU | Intel Core i5-7500 @ 3.40 GHz, 4 núcleos / 4 hilos |
| GPU | Intel HD Graphics 630 (integrada), driver 31.0.101.2141. AdapterRAM WMI 1 GiB (no es VRAM dedicada; memoria compartida) |
| RAM | 23.88 GiB |
| Disco de trabajo | C: 47.8 GiB libres |
| API gráfica | Direct3D 11 (baseline 71.2; se confirma en editor) |

Consecuencia: GPU integrada → se mantiene el **perfil conservador de 71.3** (720p/30 FPS como objetivo local medible, URP Forward, luz horneada + una linterna con sombra). 1080p/60 queda como perfil de evaluación en equipo más potente (105.2).

## Unity

| Campo | Dato |
|---|---|
| Editor | 6000.6.1f1 (`C:\Program Files\Unity\Hub\Editor\6000.6.1f1`). Carpeta 6000.6.0f1 existe sin ejecutable |
| Decisión vs target 71.2 (6000.3.9f1) | Se adopta 6000.6.1f1: es la única instalada funcional y compatible con URP 17.x; cambio ADP registrado (105.2) |
| Plantilla | `com.unity.template.urp-blank` 17.2.1 |
| Pipeline | URP `com.unity.render-pipelines.universal` 17.6.0 |
| Paquetes clave (manifest) | inputsystem 1.20.0 · ai.navigation 2.0.14 · test-framework 1.8.0 · timeline 6.6.0 · ugui 2.6.0 · pipeline 0.7.0-exp.1 (CLI) · coplaydev.unity-mcp (git, versión resuelta pendiente de lockfile) |
| Licencia | Unity Personal activa (CLI `unity license status`) |
| CLI | unity-cli 1.0.0-beta.6 (`%LOCALAPPDATA%\Unity\bin\unity.exe`) |
| Build target | Windows x64, Direct3D11 (confirmado por `SystemInfo` en editor) |

## Blender

| Campo | Dato |
|---|---|
| Ejecutable | `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` — **5.2.1 LTS**. Carpeta "Blender 4.5" existe sin ejecutable |
| Decisión vs target 71.2 (4.5 LTS) | Se adopta 5.2.1 LTS (única funcional; LTS). Enum de motores en esta versión: `BLENDER_EEVEE`, `BLENDER_WORKBENCH`, `CYCLES` |
| Unidades | METRIC, scale_length 1.0 |
| Exportador FBX | operativo (`export_scene.fbx`, -Z forward / Y up, sin leaf bones) |

## MCP Blender

| Campo | Dato |
|---|---|
| Servidor | `mcp-for-blender` v2.0.0 (`C:\Users\HP\.local\bin\mcp-for-blender.exe`), stdio, cliente Claude Code |
| Addon | `blender_mcp.py` 1.7, protocolo 7, auto-arranque activo, puerto 9876 |
| Herramientas comprobadas | `get_addon_status`, `get_scene_info`, `execute_blender_code` (crear, guardar, exportar, render) |
| Prueba de transporte (71.4 / 100.2.5) | Cubo `PROBE_Cube_1m` 1×1×1 m → `SourceArt/_probe/mcp_probe.blend` (98 348 B), `PROBE_Cube_1m.fbx` (11 836 B), `probe_viewport.png` (275 398 B, EEVEE). **Pasa** |

## MCP Unity

| Campo | Dato |
|---|---|
| Servidor | `mcpforunityserver` v10.2.0 (`mcp-for-unity.exe --transport stdio`), cliente Claude Code |
| Paquete en proyecto | `com.coplaydev.unity-mcp` vía git, fijado a commit `9dfd02a8218d` |
| Transporte | stdio (puente Unity en puerto 6400, instancia `EsneiderProtocoloLazaro@a9bd9177`). El paquete por defecto registra HTTP (127.0.0.1:8080) en scope local del proyecto; se forzó stdio (`EditorConfigurationCache.SetUseHttpTransport(false)`, `AutoStartOnLoad=true`) y se restauró la entrada stdio `unityMCP` en scope de usuario |
| Herramientas expuestas | manage_editor, manage_scene, manage_asset, manage_script, manage_gameobject, manage_components, manage_prefabs, manage_packages, execute_code, read_console, run_tests, manage_build, manage_camera (screenshot), refresh_unity, recursos `mcpforunity://…` |
| Prueba de transporte (71.4 / 100.2.5) | Import de `Assets/_Probe/PROBE_Cube_1m.fbx` → bounds 1.000×1.000×1.000 m, 12 tris, escala 1; Rigidbody 2 kg + BoxCollider; consola leída; escena `Assets/_Probe/MCP_Probe.unity` guardada. URP activo, Direct3D11, GPU Intel HD 630 (12 225 MB compartidos según SystemInfo). **Pasa** |
| Compilador `execute_code` | CodeDom (C# 6); sin Roslyn en el proyecto |

## Preset de producción (inicial, VAL)

720p, render scale 1.0, objetivo 30 FPS estables (medir tras EX-05), luz estática horneada + probes, una linterna con sombras, fog estándar, sin SSAO hasta medir, texturas hero 2K / props 512–1K, LOD y culling por sala, máx. 2 atacantes.

## Recuperación

Baseline fuente: commit `3f60e5e` + docs con bloque de instrucciones sin commitear (preservado). Destino de backup externo: **pendiente de autorización del usuario** (98.3). `.gitignore` de Unity añadido en raíz.

## Limitaciones registradas

- Python del sistema (3.14.7) sin cv2/numpy; las skills de referencia usan el runtime dedicado de skills (verificado).
- Hojas VIS/REF (82) no existen: las skills de reconstrucción por referencia quedan condicionadas a producirlas.
- No hay revisor humano distinto del usuario: estados de aceptación se registran como *Autoevaluado / Pendiente de revisión* (99.2).
