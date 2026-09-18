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

| OP-0030 | EX-03 | Write | Persistencia: `EntityState`/`WorldEvent` (88.6), `WorldStateRegistry` (registro de sesión, eventos idempotentes por (entidad, secuencia), snapshot inmutable), `SaveData`/`SaveEnvelope` (19/89.1, SHA-256), `SaveFileStore` (89.2: temporal → reabrir/validar → `File.Replace` con generaciones bak1/bak2; 89.4 recuperación y copias `.invalid-*`), `SaveValidator` (89.3), `CheckpointService` (captura fin de frame, garantía CP-06 idempotente, pipeline de carga 19), `PersistentEntity` (hidratación pickups/puertas/enemigos/movibles), `ObjectiveService` (permisos A/B/servicio/jefe/panel) | `Scripts/Core/Persistence/*`, `Scripts/World/PersistentEntity.cs` | 0 errores CS | verificado |
| OP-0031 | EX-03 | TestRunnerBridge (EditMode) | `SaveStoreTests`: ida y vuelta, rotación de generaciones, truncado → bak1 con aviso, checksum alterado, rechazos semánticos (GUID duplicado, negativo, salud >90, muerto con HP, recogido con cantidad, D29 sin jefe), versión futura conservada sin abrir, `.tmp` huérfano ignorado, idempotencia del registro | `evidencia/tests_EditMode.md` | 21/21 | verificado |
| OP-0032 | EX-03 | TestRunnerBridge (PlayMode) | `PersistencePlayTests`: QA-09 (guardar, consumir, matar, mover caja, cargar → coherente), QA-10 (continuar desde archivo, sin duplicar pickup, cargar dos veces no suma), QA-11 (activo corrupto → bak1), garantía CP-06 (una vez, no reduce), sin checkpoint en captura/acción | `evidencia/tests_PlayMode.md` | pasa | verificado |
| OP-0033 | EX-03 | corrección | `PersistentEntity.OnEnable` corría en `AddComponent` antes de asignar el GUID → registro vacío; ahora registro perezoso (`EnsureRegistered` en Start/Notify/Capture). Fuga de estado entre pruebas (registro de sesión estático) → `ResetSession` en SetUp | `PersistentEntity.cs`, tests | QA-09/10 pasan | verificado |
| OP-0034 | EX-03 | Write | Regiones: `RegionCatalog` (cadena de 7 y puertas frontera 88.1), `RegionVolume`, `RegionStreamer` (estados Unloaded→Loading→Restoring→Ready→Active→Quiescing→Unloading/Failed, una operación por región, precarga de vecinas, descarga solo segura 88.3, retención del jugador hasta Ready 89.4), `CheckpointTrigger` (identidad Player, refugio repetible), `Mechanism` (flag + precarga 88.2), `VictoryTrigger` (97), `Door` con permisos y `NavMeshObstacle` | `Scripts/World/*` | ok | verificado |
| OP-0035 | EX-03 | unityMCP · execute_code → `RegionSceneBuilder.Build()` | `BOOT.unity` (sistemas, jugador en CP-00, HUD) + `Regions/REG-*.unity` (geometría del plano por región, 141 entidades: 46 pickups + 12 documentos con soporte, 38 bots con patrulla de 2 puntos, 31 puertas, 4 mecanismos + gabinete placeholder, 10 CP, victoria) con `NavMesh` horneado por región (`REG-*_NavMesh.asset`); Build Settings actualizado | `Assets/_Game/Scenes/**` | 7 regiones, 246/38/317/45/260/40/255 tris; 38/38 bots sobre NavMesh | verificado |
| OP-0036 | EX-03 | corrección | Geometría del blockout nacía en capa Default → NavMesh regional vacío (38 bots fuera de malla); `MakeBox`/rampas ahora en `WorldStatic`. `Trigger` ignoraba al `Player` en la matriz de colisión → volúmenes/checkpoints mudos; corregido. `CharacterController.Move` durante retención de región y `remainingDistance` sin malla guardados | `BlockoutBuilder.cs`, `SandboxBuilder.cs`, `PlayerMotor.cs`, `EnemyBrain.cs` | 0 avisos en la suite | verificado |
| OP-0037 | EX-03 | TestRunnerBridge (PlayMode) | `StreamingPlayTests`: permiso → precarga C1; cruce a C1 → S2 lista antes de D07 y S1 conservada; avance en S2 → S1 descargada y C2 precargada; reentrada conserva pickup recogido (registro global) y retry lo restaura (snapshot); región inexistente falla sin romper la sesión | `evidencia/tests_PlayMode.md` | 17/17 total | verificado |
| OP-0038 | EX-03 | unity-cli eval (Play Mode) | BOOT jugado: estados de regiones y capturas al despertar en S1 y al cruzar a C-01 | `SourceArt/_evidence/EX-03/*.png` | evidencia | ejecutado |

| OP-0039 | EX-04 | Skill · blender-skill-harmonizer / blender-pro-workflow | Sin hojas VIS/REF externas (82 pendiente): orden genérico de producción; las skills de reconstrucción por referencia quedan NA para esta etapa | — | plan registrado | verificado |
| OP-0040 | EX-04 | Write | Biblioteca `bpy` `SourceArt/Scripts/esn_lib.py`: primitivas por `bmesh` con pivote controlado, cables por polilínea, materiales PBR procedurales (41.2 roughness, desgaste por ruido, bump), UV smart-project por pieza, bake a BaseColor/Roughness/Metallic(vía emisión)/Normal (41.1), armadura por hueso rígido (36.4), clips por NLA (Blender 5: acciones por capas), export FBX 24.2 (-Z/Y, sin leaf bones, NLA→clips), hoja de 3 vistas (45.3), informe JSON. Operadores bajo `temp_override` porque el socket MCP carece de área activa | `SourceArt/Scripts/*.py` | 16 assets fabricados | verificado |
| OP-0041 | EX-04 | blender · execute_blender_code (cola `queue_runner.py` por `bpy.app.timers`) | BOT-01 Vigía (36 piezas, 10.6k tris, 1.29 m, 5 clips: Idle/Walk/Anticipation 1.1 s/Net/Death), BOT-02 Custodio (42, 7.9k, 2.22 m, 6 clips), BOT-03 Archivista (34, 8.2k, 3.10 m, 7 clips: cuatro firmas 60.4), CHR-01 brazos (88 piezas: falanges/nudillos/uñas/tendones/puño/pulsera, 15.2k, 5 clips), WPN-01 varilla (doblez, agarre descubierto), WPN-02 pistola (corredera/cargador/gatillo/guardamonte/tornillos), WPN-03 escopeta (bombeo/culata/puertos), WPN-04 linterna (lente/reflector/junta/switch), PRP jeringa/ración, OBJ-001 criocámara (32 piezas, tapa con bisagras + clip Cryo_Open 2.4 s, pantalla, manifold), OBJ-041 jaula (barras ≥12 cm, puerta con bisagras + Cage_Open, cierre, placa), OBJ-070 puerta corrediza (dos hojas + riel + motor + sensor, Door_Open 2 s), OBJ-059 terminal, OBJ-043 camilla (ruedas/horquilla/colchón comprimido/barandas/IV), OBJ-029 carro | `SourceArt/Blender/*.blend`, `Assets/_Game/Art/Models/*.fbx`, `Art/Textures/*_{BaseColor,Roughness,Metallic,Normal}.png`, `SourceArt/_evidence/EX-04/*` | 16/16, 0 fallos; tiempo de cola 55 min (horneado 1024 hero / 512 props) | verificado |
| OP-0042 | EX-04 | unityMCP · execute_code → `AssetIntegrator.Integrate` | Import FBX (escala de archivo, normales/tangentes, Generic, ejes horneados), material URP Lit por asset con BaseMap/Normal y `_MetallicGlossMap` empaquetado (Metallic R + Smoothness=1−Roughness en A), prefab con collider simplificado, informe `*_unity.json` (tris/clips/dims) | `Prefabs/{Enemies,Player,Weapons,Environment}/*.prefab`, `Art/Materials/Assets/M_*.mat` | 16 prefabs; clips presentes (5/6/7/5/2/1/1) | verificado |
| OP-0043 | EX-04 | Write | `EnemyAnimator` (Playables: FSM→clip, crossfade 0.2 s sin acortar telegraph 86.5), `ViewmodelController` (brazos + arma activa bajo cámara, clips por acción, head bob desactivable), `DoorAnimated` (OBJ-070 con colliders por hoja), `HeroDressing` (criocámara en S1-R01, carro Rigidbody en taller, 8 jaulas, 3 camillas, terminales en DOC, puertas de 2.8 m sustituidas, modelos en pickups), `ShowcaseBuilder` (`Art_Showcase` con luz neutra/juego conmutable tecla L) | `Scripts/**` | compila | verificado |
| OP-0044 | EX-04/05 | Write + runtime Python (numpy/scipy) + SAPI | Banco de audio ORIGINAL sintetizado (72.2): 91 WAV 48 kHz/24 bit (pasos Vigía/Custodio/Archivista, cargas de red 1.1/1.2 s y rayo 1.0 s, releases/impactos, cuatro firmas del boss, pasos Esneider por 5 superficies ×4, respiraciones, armas y mecanismos, 8 ambientes en loop por espacio 50.1, puerta inicio/loop/fin, alerta 1.8 s, checkpoint) + megafonía con guion 5.2 (voz local SAPI Sabina + receta 72.3: pasaaltos 300 Hz, corte 5 kHz, saturación baja, reverb 2 s). Manifiesto 72.4 en `docs/produccion/AUDIO_MANIFEST.json`. Identificado como generado, no como audio final | `Assets/_Game/Audio/**`, `SourceArt/Audio/gen_audio.py` | 91 archivos | verificado |
| OP-0045 | EX-04/05 | unityMCP · execute_code → `AudioSetup.Setup()` | Mezclador `EsneiderMixer` con Master/Ambient/Enemies/Weapons/Voice/UI (API interna `AudioMixerController` por reflexión, documentado), `AudioBankSet` con 55 bancos/91 clips, importación (ADPCM mono para SFX, Vorbis streaming para beds). `AudioService` (pool 24, prioridad señal mortal > voz > armas > locomoción > ambiente, sin repetición inmediata, jitter ±4 %/±1.5 dB), `AudioEvents` (ruido lógico/FSM → bancos), `EnemyFootsteps` por distancia, `RegionAudio` (bed por región con blend 1.5 s + AudioReverbZone) | `Assets/_Game/Audio/*.asset`, `Scripts/Audio/*` | ok | verificado |

| OP-0046 | EX-04 | unityMCP · execute_code | Regeneración de `Combat_Sandbox`, `BOOT` + 7 regiones (bots con visual hero + `EnemyAnimator` + pasos; vestido hero: OBJ-001 en S1-R01, OBJ-029 Rigidbody en taller, 8 jaulas, 3 camillas, terminales en DOC-01/07/09/11, 22 puertas OBJ-070 animadas con colliders por hoja y obstáculo NavMesh, modelos en pickups; `RegionAudio` por región) y `Art_Showcase` (16/16, luz neutra/juego con tecla L, jugador con viewmodel) | `Scenes/**` | ok | verificado |
| OP-0047 | EX-04 | corrección | `GetComponent<T>() ?? AddComponent<T>()` falla con el falso nulo del editor (MissingComponentException en `Volume_REG-S1`); 10 usos sustituidos por `GetOrAdd<T>()` (`ComponentExtensions`) | `Scripts/**` | suite verde | verificado |
| OP-0048 | EX-04 | TestRunnerBridge | Suite tras integración: 21 Edit Mode + 17 Play Mode | `evidencia/tests_*.md` | 38/38 | verificado |
| OP-0049 | EX-04 | unity-cli eval (Play Mode) | Capturas en motor: showcase con luz neutra (bots y props), luz de juego + linterna real con brazos/escopeta en viewmodel, S1 con criocámara y puerta D01 hero | `SourceArt/_evidence/EX-04/unity/*.png` | evidencia | ejecutado |
| OP-0050 | EX-04 | Read (PNG) + blender · execute_blender_code (`queue_runner.py`) | **Defecto detectado y corregido**: el smart-project por pieza solapaba todas las islas en el mismo atlas 0–1, así que los mapas horneados eran ruido (manchas negras en criocámara, Vigía oscuro). `uv_project_all` (smart project multi-objeto, atlas compartido) + rehorneado completo de los 16 assets; hojas de 3 vistas rehechas | `esn_lib.py`, `finish_asset.py`, `Art/Textures/*.png`, `SourceArt/_evidence/EX-04/*` | 16/16 en 11 min (03:45→03:56); atlas verificado a ojo (islas separadas, texturas coherentes) | verificado |
| OP-0051 | EX-04 | unityMCP · execute_code → `AssetIntegrator.Integrate` ×16 + `SandboxBuilder/RegionSceneBuilder/ShowcaseBuilder.Build()` | Reimport de FBX/texturas, materiales y prefabs regenerados; escenas reconstruidas con el cableado EX-05 | prefabs, materiales, escenas | tris 10588/7864/8202/15232…; clips 5/6/7/5/2/1/1; 0 avisos | verificado |
| OP-0052 | EX-05 | Write + unityMCP · `TestRunnerBridge` | `NarrativePlayTests` (EVT-01 política U: sin control durante la apertura, omisible, CP-00 confirmado con EVT-01 en el snapshot, restaurar no repite; EVT-C1: D06 → DETECTADO/O03/activación de bots, una sola vez). Correcciones que destapó: el streamer reactivaba el control tras la apertura (ahora la apertura espera `Ready`); `PlayerController` consumía la pulsación antes de la corrutina (lectura directa de teclado + `RequestSkip`); el trigger CP-00 confirmaba antes que la apertura (el test espera el commit de la apertura) | `Tests/PlayMode/NarrativePlayTests.cs`, `OpeningSequence.cs` | Edit 21/21, Play 19/19 (`evidencia/tests_*.md` 03:59/04:07) | verificado |
| OP-0053 | EX-05 | Write `EvidenceCapture` + unityMCP · execute_code | Captura automática de Game View en Play (EditorPrefs sobrevive al domain reload) → `docs/produccion/evidencia/*.png`. Destapó que `PlayerLook`/`PlayerController` sobreescribían el pivote de cámara cada frame (la apertura no se veía tumbada): ahora solo cuando la mirada/movimiento están habilitados | `evidencia/EX-04_showcase_atlas_fix.png` (bots/props con atlas corregido), `evidencia/EX-05_boot_opening.png` (vista tumbada, negro parcial 0–8 s) | evidencia | verificado |
| OP-0054 | EX-05 | Write `PlayerBuilder` + unityMCP · execute_code (`BuildPipeline.BuildPlayer`) | Build Windows x64 Release (sin profiler, 91.4) con BOOT + 7 regiones; `Builds/` ignorado en git; informe con commit git, duración, tamaño | `evidencia/build_Release.json` | Succeeded, 472 s, 145 MB, 0 errores, 34 avisos (commit 4e9c9da) | verificado |
| OP-0055 | EX-05 | Bash · `EsneiderProtocoloLazaro.exe -autotest` (ruta automática S1, 60 s tras 2 s de warmup, 1280×720 ventana, vsync 0, quality PC) | Medición 91.4 en el equipo real (i5-7500 / HD 630 / D3D11): **mediana 14.7 ms (68 fps), p95 19.7 ms, 3 hitches >100 ms** (mín. 0.35 fps: pausa aislada de carga inicial de región, se registra sin borrar), 3699 frames, reservado 540 MB / asignado 255 MB. Sin excepciones en el log del jugador | `evidencia/perf_Release_S1_C1.json`, `evidencia/player_Release_autotest.log` | cumple perfil local 720p/30 (≤33.3 / ≤40 ms) en el tramo S1; los otros 5 tramos y la sesión de 30 min quedan para EX-08 | verificado |
| OP-0056 | EX-05 | Write | `PerfProbe`: 1280×720 en `-autotest`, omite la apertura para no disputar la posición, registra vsync/quality/minFps; BOOT muestrea 62 s | `Core/PerfProbe.cs`, `RegionSceneBuilder.cs` | compila | verificado |

## Gate EX-05

| Requisito 101.1 | Estado | Evidencia |
|---|---|---|
| Un tramo que reúna arte/combate/audio/save | Pasa | BOOT→REG-S1/REG-C1: criocámara hero + apertura EVT-01, Vigía/Custodio con FSM y clips, bancos de audio + PA en OBJ-065, CP-00/CP-01 con snapshot; `NarrativePlayTests`, `StreamingPlayTests`, `PersistencePlayTests` |
| Performance destino medida | Pasa (tramo S1) | OP-0055: build real, no editor; 720p/30 cumplido con margen |
| Contratos PIL 74.2 | Ver tabla | abajo |

| REQ-PIL | Estado | Evidencia / pendiente |
|---|---|---|
| PIL-01 manos, cámara, salud | Pasa | brazos CHR-01 en viewmodel, `PlayerLook`, `Health`; build ejecutada |
| PIL-02 criocámara abre con gesto/huella | Parcial | abre por clip `Cryo_Open` dentro de EVT-01; el gesto de huella (interacción) no está implementado; malla estado "Revisar" (no Tier A) |
| PIL-03 linterna F, cono limitado | Pasa (código, sin prueba automática) | `PlayerController` alterna `Light` (spot 45°); pickup WPN-04 |
| PIL-04 varilla, 3 golpes sin daño duplicado | Pasa | QA01 + AttackID dedup (`CoreContractTests`) |
| PIL-05 Vigía FSM completa | Pasa | `EnemyAiPlayTests` (sospecha→confirmación→telegraph→red, búsqueda), muerte en QA01 |
| PIL-06 Custodio 6 golpes, rayos 30 | Pasa | QA01, QA02 (90/60/30/0) |
| PIL-07 puerta/altavoz: detección una vez, voz y alerta | Pasa | `Detection_FiresOnceWhenD06Opens_ActivatesUnits` |
| PIL-08 carro Rigidbody + superficies | Parcial | carro OBJ-029 con Rigidbody y `PhysicsImpactLogger`, `SurfaceTag`; sin prueba automática de empuje/fricción → EX-06 |
| PIL-09 salud, jeringa, derrota | Pasa | QA08, QA04 (captura ≤2.5 s) |
| PIL-10 snapshot/retry | Pasa | QA09/QA10/QA11, `ReentryKeepsChanges_RetryRestoresSnapshot` |
| PIL-11 luz neutra y de terror | Pasa | `Art_Showcase` (tecla L) y BOOT; capturas EX-04/EX-05 |
| PIL-12 sin placeholders como finales | Pasa | `AUDIO_MANIFEST.json` (síntesis declarada), assets "Revisar" (gate EX-04) |
| PIL-13 build + profiler en hardware documentado | Pasa (Release) | OP-0054/0055; build Development con profiler pendiente para diagnóstico (EX-08) |
| PIL-14 evidencia de contactos | Pendiente | mano-grip, pie-suelo, tapa y puerta/riel sin captura dedicada → EX-06 (checklist 104) |

Decisión de gate: **Pasa con pendientes no bloqueantes** (PIL-02 gesto de huella, PIL-08 prueba física, PIL-14 evidencia de contactos, build Development). Ninguna tasa FPS inventada: el único dato de rendimiento procede de la build Release en el equipo real.

## Gate EX-04

| Requisito 101.1 | Estado | Evidencia |
|---|---|---|
| Referencias VIS/REF revisadas | Parcial | Sin concept art externo: las hojas de 3 vistas de cada asset (`SourceArt/_evidence/EX-04/*_front/side/iso.png`) actúan como REF interna; las 19 hojas VIS de 82 siguen pendientes de decisión artística (HUM) |
| Brazos, tres robots, armas y seis props hero importados con rig/UV/PBR | Pasa (calidad: Blockout+/Revisar) | 16/16 assets con `.blend`, FBX, UV por pieza, 4 mapas horneados, materiales URP, prefabs, clips; informes `*_report.json` y `*_unity.json` |
| Evidencia neutra/juego | Pasa | Hojas Blender (luz neutra) + capturas Unity showcase neutra/juego y S1 in-game |

Decisión de gate: **Pasa con estado artístico "Revisar"** (99.2: Autoevaluado / Pendiente de revisión). Honestidad de acabado: los assets son construcciones procedurales por piezas con función, pivotes, rig rígido y PBR horneado; no alcanzan todavía el estándar Tier A de 33–41 (sin escultura high/low, sin bake de normal desde high, texturas por ruido procedural en vez de pintado con causa, manos sin loops de deformación). Se declaran como base de iteración, no finales (46.5). Pendientes concretos: retopología/escultura de manos y rostro de robots (35.2/36), texturizado con desgaste por causa (41.3), poses de arma calibradas desde cámara (35.2), LOD (43), hojas VIS (82).

## Gate EX-03

| Requisito 101.1 | Estado | Evidencia |
|---|---|---|
| Registro global, save/backup | Pasa | OP-0030/0031/0032 |
| Siete regiones y puertas frontera | Pasa | OP-0034/0035/0037 |
| Reentrada y retry distintos | Pasa | `ReentryKeepsChanges_RetryRestoresSnapshot_NoDuplication` |
| Cero duplicación | Pasa | QA-10, garantía CP-06, eventos idempotentes |
| Fallo de carga seguro | Pasa | `UnknownRegionFailsSafely`, truncado/corrupto → backup |

Decisión de gate: **Pasa**. Pendientes: distancia de precarga por polilínea (88.2: 8/12 m) implementada como vecindad por volumen, a refinar en EX-05 con medición; oclusión acústica por portales completa (78.1) pendiente; migraciones `vN→vN+1` (89.5) solo esqueleto (schemaVersion); prueba de 20 ciclos de carga con memoria estable pendiente para EX-05/08.

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
