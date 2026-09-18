# Matriz del taller (25 / FIN-12)

| Requisito | Implementación | Evidencia (archivo / prueba) | Estado |
|---|---|---|---|
| Escena 3D organizada | BOOT + 7 escenas de región (`Systems`, `Entities/{Furniture,…}`, `Volume_*`), sectores agrupados por planta | `Assets/_Game/Scenes/**`, `RegionSceneBuilder.cs`; capturas `evidencia/EX-06_*.png` | Demostrado |
| Objeto mediante teclado | Esneider (WASD/Shift/Ctrl/Espacio, F linterna, E interactuar, 1-2-3 armas, R, Q) con Input System | `Player/PlayerInput.cs`, `PlayerMotor.cs`, `PlayerController.cs`; `SandboxPlayTests` | Demostrado |
| Rigidbody funcional | Carros OBJ-029 (M026 taller, M035 patio) con masa 24 kg, centro de masa bajo, amortiguación y colisión continua | `FurnitureBuilder.cs` (physics=true), `SandboxFactory` (caja física) | Demostrado (sin prueba automática de empuje: PIL-08) |
| Colisión por código | `PhysicsImpactLogger.OnCollisionEnter` → ruido (`NoiseSystem`) + contador `physicsImpacts` en la línea de resultado | `World/PhysicsImpactLogger.cs`, `GameFlowController.EndAttempt` | Demostrado |
| Trigger funcional | `CheckpointTrigger` (snapshot), `RegionVolume` (streaming), `RoomEvent` (eventos U/A), `VictoryTrigger` (ESCAPE) — todos comprueban la entidad principal del jugador | `PersistencePlayTests`, `SectorPlayTests`, `CampaignRunPlayTests` | Demostrado |
| Variables e Inspector | Definiciones ScriptableObject (95): vida, daño, velocidades, telegraphs, cooldowns, capacidad de munición, jefe | `Core/Data/*Definition.cs`, `Assets/_Game/Data/**`, `DATA_BASELINE.md` | Demostrado |
| Modificar componente | `Light.enabled` de la linterna (F); `ShowcaseLightToggle` (L) conmuta luz neutra/juego | `PlayerController.cs:59`, `World/ShowcaseLightToggle.cs` | Demostrado |
| Cámara coherente | Primera persona: yaw en cuerpo, pitch en pivote con límites, FOV vertical 75° (70–100), sin balanceo obligatorio | `Player/PlayerLook.cs`, `ViewmodelController.cs`; capturas in-game | Demostrado |
| 10 materiales | Materiales URP por asset (`M_BOT-01…`, 16) + blockout/kit (`Blockout_*`, `Kit_*`) | `Assets/_Game/Art/Materials/**` | Demostrado (≥ 26 materiales) |
| Physic Material | `SUR-RUB` (goma, fricción 0.8/0.7) y `SUR-WET` (carril mojado 0.55/0.45) sobre superficies del sandbox; `SurfaceTag` por familia de mobiliario | `SandboxFactory.cs:42-43`, `World/SurfaceTag.cs` | Demostrado en sandbox; diferencia de deslizamiento observable en `Combat_Sandbox` |
| 5 modelos externos | 16 FBX importados desde Blender (`SourceArt/Blender/*.blend` → `Assets/_Game/Art/Models/*.fbx`) con `AssetIntegrator` | `OP-0041/0042/0051`, `SourceArt/_evidence/EX-04/*` | Demostrado como modelos originales de Blender; **la aceptación de "externo = propio en Blender" debe confirmarse con el docente** |
| Condición final | Muerte (red/daño), captura y escape; una línea de consola por intento con Resultado/Sector/Vida/Enemigos/Disparos/Impactos/Tiempo y línea VICTORIA con estadísticas | `GameFlowController.EndAttempt`, `MenuController.ShowVictory`, `MenuPlayTests`, `CampaignRunPlayTests` | Demostrado |
| Entregables | Proyecto completo en el repositorio, README/controles/créditos/licencias, build Windows regenerable, informe QA y acta | `docs/entrega/*`, `Builds/Windows/Release` | Preparado; **publicación (Drive/Moodle) es decisión humana** (106.3) |
