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

| OP-0013 | EX-01 | git | Commit baseline `f406e34` (120 archivos, sin Library) | repo | ok | verificado |
| OP-0014 | EX-01 | Write | `bunker_plan.json` (68/88.1/93/96 transcritos: 6 plantas, 22 salas, 28 circulaciones, 2 escaleras, 31 puertas, 3 conectores, 38 spawns, 46 pickups, 12 DOC, 10 CP, 5 mecanismos, 4 pilares, exterior) | `Assets/_Game/Data/LevelPlan/bunker_plan.json` | validado | verificado |
| OP-0015 | EX-01 | Write + unityMCP · refresh | Definiciones 95.1 (`Definitions.cs`), `LevelPlan.cs`, `DataValidator.cs` (95.2), `LevelMarker.cs`, `BlockoutBuilder.cs`, `BaselineDataCreator.cs` | `Assets/_Game/Scripts/**` | 0 errores CS | verificado |
| OP-0016 | EX-01 | manifest | Pin a hash corto `#9dfd02a8218d` rompió la resolución git del paquete MCP (desapareció de PackageCache); revertido a URL sin hash. Pendiente: pin con hash completo | `Packages/manifest.json` | resuelto tras `Client.Resolve()` | verificado |
| OP-0017 | EX-01 | unityMCP · execute_code → `BaselineDataCreator.Create()` | 158 assets en `Data/Definitions` (player, 3 armas, 2 bots, boss, 9 superficies, 25 regiones, 10 CP, 26 eventos, dificultad Normal, catálogo); capas 20.3 en TagManager; export `DATA_BASELINE.md` | `Assets/_Game/Data/Definitions/**`, `ProjectSettings/TagManager.asset`, `docs/produccion/DATA_BASELINE.md` | validador datos PASA 0/0; plano PASA 0/0 | verificado |
| OP-0018 | EX-01 | unityMCP · execute_code → `BlockoutBuilder.Build()` | Escena `Bunker_Blockout` rasterizada a 0.2 m: 6 plantas + 3 conectores, muros/estructura, losas con huecos de escalera, dinteles, rampas STA-01/02, pilares, exterior; 141 marcadores con GUID estable | `Assets/_Game/Scenes/Bunker_Blockout.unity`, `Art/Materials/Blockout/*` | 2.2 s; 305 renderers | verificado |
| OP-0019 | EX-01 | unityMCP · execute_code (Physics) | 141 marcadores: esfera libre + suelo debajo. Único fallo CP-02 (8,24) en esquina muro/enlace → corrección PL-CP02-01 a (10,25) | `bunker_plan.json` | 141/141 tras corrección | verificado |
| OP-0020 | EX-01 | unityMCP · execute_code (NavMesh) | Primera pasada: 6 tramos parciales en puertas frontera; causa: banda del conector se extendía 2.25 m + muro detrás del plano de puerta. Corregido en `BuildConnector` (clamp al plano de puerta) | `BlockoutBuilder.cs` | 24/24 tramos completos; CP-00→VICTORY 419 m; ruta de objetivos 760 m | verificado |
| OP-0021 | EX-01 | unityMCP · execute_code (cámara temporal → PNG 1280×720) | 9 capturas: vista general, P01–P06, STA-01, interior C-01 y S1-R01 | `SourceArt/_evidence/EX-01/*.png` | evidencia | verificado |

| OP-0022 | EX-02 | Write (26 scripts) + asmdefs | Núcleo: `GameFlowController` (estados 20.1 + línea de consola 25), `Health` (AttackID + invulnerabilidad 0.65 s), `ActionTransaction` (Begin/Commit/Cancel/Complete 86.6), `NoiseSystem` (78.1, puerta 35%). Jugador: `PlayerInput` (mapa 9 en código), `PlayerMotor` (CharacterController, agachado con techo, resistencia 100/22/18, empuje limitado), `PlayerLook`, `Inventory` (18/11.1), `PlayerActions` (equipar/ataque/recargas 86.3-86.4/curas 10), `PlayerController` (captura ≤2.5 s, derrota, reinicio). Combate: `Projectile` (barrido, pool). IA: `EnemyPerception` (78.1), `EnemyBrain` (FSM 78.2), `EncounterDirector` (2 slots, 0.65 s). Mundo: `Pickup` parcial, `Door`, `PhysicsImpactLogger`, `SandboxFactory`, `RuntimeNavMeshBaker`. UI: `HudController` (placeholder uGUI) | `Assets/_Game/Scripts/**`, `Esneider.Runtime/Editor/Tests.*.asmdef` | 0 errores CS | verificado |
| OP-0023 | EX-02 | diagnóstico | Assets de definiciones perdían `m_Script` ("No script asset for GameDataCatalog"): Unity exige un archivo por clase con el mismo nombre. `Definitions.cs` e `Interactables.cs` repartidos en archivos propios; assets regenerados (GUIDs nuevos; prefabs reconstruidos) | `Scripts/Core/Data/*.cs`, `Scripts/World/*.cs` | catálogo carga boss con 4 ataques | verificado |
| OP-0024 | EX-02 | unityMCP · execute_code → `SandboxBuilder.Build()` | Escena `Combat_Sandbox` 12×12 m con pilar, carriles goma/mojado (Physic Material), caja Rigidbody 20 kg con colisión por código, 8 pickups, Esneider (cápsula 1.75/0.3, cámara FOV 75, linterna Light), Vigía 1.25 m y Custodio 2.15 m placeholder con NavMeshAgent; prefabs `Player_Esneider`, `Vigia_Placeholder`, `Custodio_Placeholder`; matriz de colisión 20.3 aplicada; escena en Build Settings | `Scenes/Combat_Sandbox.unity`, `Prefabs/**` | ok | verificado |
| OP-0025 | EX-02 | unityMCP · run_tests (EditMode) | 13 pruebas de contrato: commits únicos, cancelación antes/después, AttackID, invulnerabilidad, 90→60→30→0, 3/6 golpes, 5/20→12/13, 2/10→4/8, recogida parcial, arma con 10+10 | `Tests/EditMode/CoreContractTests.cs` | 13/13 | verificado |
| OP-0026 | EX-02 | `TestRunnerBridge` (TestRunnerApi → archivo) | `run_tests` de MCP quedaba huérfano al entrar en Play Mode (domain reload mata el puente stdio). Runner propio escribe `docs/produccion/evidencia/tests_*.md` | `Scripts/Editor/Tests/TestRunnerBridge.cs` | resultados en disco | verificado |
| OP-0027 | EX-02 | TestRunnerBridge (PlayMode) | QA-01 (3/6 golpes reales con varilla), QA-02 (tres rayos), QA-03 (red bloqueada por pilar), QA-04 (captura → derrota ≤2.5 s), QA-06 (recarga cancelada antes/después de 1.35 s), QA-08 (cura a vida llena / cancelación), pistola bloqueada por cobertura + escopeta 8×7.5 sumados una vez, IA: sospecha acumulada→telegraph→una emisión→captura→DERROTA_RED; pérdida de visión→búsqueda en última posición vista | `Tests/PlayMode/*.cs`, `evidencia/tests_PlayMode.md` | 9/9 | verificado |
| OP-0028 | EX-02 | corrección | `EnemyBrain.Chase` copiaba la posición actual del jugador con percepción de hasta 0.1 s (omnisciencia); ahora solo `EnemyPerception.Sense` fija `lastKnownPosition` al ver | `EnemyBrain.cs` | test de búsqueda pasa | verificado |
| OP-0029 | EX-02 | unity-cli eval (Play Mode) | Sandbox jugado en editor: capturas de Game View y estados de bots | `SourceArt/_evidence/EX-02/*.png` | evidencia | ejecutado |

## Gate EX-02

| Requisito 101.1 | Estado | Evidencia |
|---|---|---|
| Movimiento, armas, dos bots, telegraphs, inventario, interacción, ActionID | Pasa | OP-0022/0024 |
| Tres/seis golpes | Pasa | QA-01 Play Mode + HealthTests |
| Tres rayos | Pasa | QA-02 + HealthTests (90→60→30→0 con invulnerabilidad 0.65 s) |
| Captura acotada | Pasa | QA-04 y test IA (≤2.5 s, DERROTA_RED) |
| Cancelaciones coherentes | Pasa | QA-06/QA-08 + ActionTransactionTests |
| Sin arte masivo | Cumple | cápsulas/cubos placeholder declarados |

Decisión de gate: **Pasa**. Pendientes registrados: HUD en uGUI provisional (migrar a UI Toolkit en EX-07); animaciones/clips ausentes (EX-04); velocidades del jugador de la sección 9 aplicadas (3/5/1.5 m/s) como VAL; `PlayerInDarkness` es un flag global hasta los volúmenes de visibilidad (EX-05/06); oclusión acústica por portales básica (raycast + puerta 35%).

## Gate EX-01

| Requisito 101.1 | Estado | Evidencia |
|---|---|---|
| Definiciones 95 instanciadas, ownership y GUIDs | Pasa | OP-0017, `DATA_BASELINE.md` (GUIDs MD5 de `ESNEIDER:<ID>`) |
| Catálogos sin duplicados | Pasa | DataValidator 0 errores (IDs, rangos, 60/20=3, 120/20=6, 90/30=3, boss 60/40, garantía CP-06 ≤ capacidad, 140 balas/50 cartuchos, 23V/14K/1B) |
| Seis plantas de 68 en blockout completo transitable | Pasa | OP-0018/0020: NavMesh CP-00→VICTORY PathComplete |
| Correcciones de plano registradas | Pasa | PL-CP02-01 (CP-02 → (10,25)); D29-EXT como hoja exterior de D29; alturas útiles ADP: P01 4.5, P02 4, P03 8, P04 5.5, P05 5, P06 7; escaleras como rampas de colisión con descansillos, eje Z, STA-01 arranca sur / STA-02 arranca norte |

Decisión de gate: **Pasa**. Pendientes no bloqueantes: pin de paquete MCP con hash completo; velocidades del jugador (sección 9) marcadas VAL en `Player_Esneider`; relleno de estructura entre rectángulos es sólido en blockout (68.1: "circulación/estructura"), a revisar en montaje de salas (EX-06).

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
