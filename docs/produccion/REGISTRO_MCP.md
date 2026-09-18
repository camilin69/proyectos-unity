# Registro de uso MCP y evidencia (sección 100.6 / 94.4)

Formato: ID · etapa · servidor/herramienta real · operación · archivos afectados · resultado · evidencia. Estados: ejecutado / inspeccionado / verificado.

| ID | Etapa | Servidor · herramienta | Operación | Archivos | Resultado | Estado |
|---|---|---|---|---|---|---|
| OP-0001 | EX-00 | blender · get_addon_status | Inventario de capacidades del addon | — | 5.2.1 LTS, addon 1.7, protocolo 7, 11 capacidades | verificado |
| OP-0002 | EX-00 | blender · get_scene_info | Escena por defecto (Cube/Light/Camera) | — | 3 objetos, unidades METRIC | inspeccionado |
| OP-0003 | EX-00 | blender · execute_blender_code | Colección `MCP_PROBE`, cubo 1 m, guardar y exportar FBX (-Z/Y, sin leaf bones) | `SourceArt/_probe/mcp_probe.blend` (98 348 B), `PROBE_Cube_1m.fbx` (11 836 B) | dims 1.0×1.0×1.0 m | verificado |
| OP-0004 | EX-00 | blender · execute_blender_code | Render EEVEE 800×600 de evidencia | `SourceArt/_probe/probe_viewport.png` (275 398 B) | motor `BLENDER_EEVEE` (5.2 no expone `_NEXT`) | verificado |
| OP-0005 | EX-00 | unity-cli 1.0.0-beta.6 · `projects create` | Proyecto `EsneiderProtocoloLazaro` plantilla `urp-blank` 17.2.1, editor 6000.6.1f1 | `EsneiderProtocoloLazaro/` | success | verificado |
| OP-0006 | EX-00 | unity-cli · `pipeline install` / `open` | `com.unity.pipeline` 0.7.0-exp.1; editor abierto, estado `ready` puerto 7800 | `Packages/manifest.json` | success | verificado |
| OP-0007 | EX-00 | manifest (edición) | Añadido `com.coplaydev.unity-mcp` (git `CoplayDev/unity-mcp?path=/MCPForUnity`, commit `9dfd02a8218d`) | `Packages/manifest.json`, `packages-lock.json` | resuelto, 0 errores CS | verificado |
| OP-0008 | EX-00 | unity-cli · `command eval` | El paquete había registrado transporte HTTP (8080) y eliminado la entrada stdio del cliente; se forzó `EditorConfigurationCache.SetUseHttpTransport(false)`, `AutoStartOnLoad=true`, `Bridge.StartAsync()`; se restauró `claude mcp add -s user unityMCP` (stdio) | `~/.claude.json`, EditorPrefs | puente stdio en 6400, instancia `EsneiderProtocoloLazaro@a9bd9177` | verificado |
| OP-0009 | EX-00 | unityMCP · recursos `instances`, `editor/state` | Lectura de estado | — | `ready_for_tools: true`, escena SampleScene | inspeccionado |
| OP-0010 | EX-00 | unityMCP · read_console | Errores/warnings previos | — | solo fallos del intento HTTP (esperados) | inspeccionado |
| OP-0011 | EX-00 | PowerShell + unityMCP · refresh_unity | Copia del FBX de ensayo y estructura `Assets/_Game` (36 carpetas, sección 20) + `SourceArt/{Blender,Textures,Scripts,_evidence}` | `Assets/_Probe/PROBE_Cube_1m.fbx`, `Assets/_Game/**` | refresh idle | ejecutado |
| OP-0012 | EX-00 | unityMCP · execute_code (CodeDom) | Escena nueva, instancia del FBX, Rigidbody 2 kg + BoxCollider, plano, guardar escena | `Assets/_Probe/MCP_Probe.unity` | bounds 1.000×1.000×1.000 m, 12 tris, escala 1, URP activo, D3D11, GPU Intel HD 630 (12 225 MB compartidos reportados) | verificado |

## Gate EX-00

| Requisito | Estado | Evidencia |
|---|---|---|
| MCP-DEST-01 reconocer destino y ambos servidores | Pasa | OP-0001, OP-0008/09, `TECH-BASELINE.md` |
| Prueba de transporte 71.4 (Blender crea/guarda/exporta; Unity importa/inspecciona/Rigidbody/logs/escena) | Pasa | OP-0003, OP-0010, OP-0012 |
| Baseline y backups 98 | Parcial | `.gitignore` creado; commit de baseline y destino de backup externo pendientes de decisión del usuario |
| Formulario 105.1 | Completo salvo backup externo | `TECH-BASELINE.md` |
| Matriz de skills (instrucción inicial) | Completa | `SKILLS_MATRIZ.md` |

Decisión de gate: **Pasa con pendientes no bloqueantes** (backup externo autorizado por el usuario; commit inicial).

## Limitaciones y notas

- `execute_code` de Unity compila con CodeDom (C# 6) al no haber Roslyn; para lógica compleja se usarán scripts `.cs` reales + `refresh_unity`.
- Las herramientas de unityMCP en este cliente exigen todos los parámetros explícitos (cadenas vacías / valores por defecto), no omitidos.
- `unity command eval` corta en 5 s de hilo principal: no bloquear con `Task.Wait`.
- Blender 5.2 no expone `BLENDER_EEVEE_NEXT`; usar `BLENDER_EEVEE` o `CYCLES`.
