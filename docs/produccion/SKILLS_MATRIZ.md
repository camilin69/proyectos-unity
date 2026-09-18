# Matriz de skills — producción "Esneider: Protocolo Lázaro"

Fecha: 2026-09-17 · Etapa: EX-00 · Estado: baseline (se actualiza por etapa; sección 106 del maestro).
Fuente verificada: `C:/Users/HP/.claude/skills/<nombre>/SKILL.md` — 69/69 presentes. Runtime auxiliar de skills Blender: `C:/Users/HP/.claude/skill-runtimes/blender/Scripts/python.exe` (Python 3.11.16, cv2 5.0.0, numpy 2.4.6, Pillow 12.3.0, scipy 1.17.1) verificado. Todo `bpy` se ejecuta vía MCP `blender` (`execute_blender_code`), nunca con ese intérprete.

Columnas: condición de activación → entregable → evidencia exigida. Estado: `P` pendiente · `A` aplicada · `NA` no aplicable (motivo).

## Blender, referencias y control de calidad

| Skill | Etapa / asset | Condición de activación | Entregable | Evidencia | Estado |
|---|---|---|---|---|---|
| text-to-blender | EX-04, EX-06 · todo asset | Cualquier fabricación en Blender | Orquestación y encadenado de sub-skills | Registro MCP por asset | P |
| blender-skill-harmonizer | EX-04 inicio | Antes del primer asset hero; solape entre skills | Plan de precedencia y handoffs | Sección en registro de producción | P |
| blender-pro-workflow | EX-04, EX-06 | Asset multi-fase (modelo+material+UV+export) | Orden de trabajo por asset | Checklist por ficha OBJ | P |
| blender-modeling | EX-04/06 · OBJ/CHR/BOT/WPN | Geometría con espesor y piezas funcionales | `.blend` fuente en `SourceArt/Blender` | Métricas (dims, tris) + captura | P |
| blender-materials | EX-04/06 | Look-dev PBR según 41 | Principled BSDF exportable | Captura luz neutra | P |
| blender-uv-texturing | EX-04/06 | UV0/UV1, bake, atlas por 40.3/40.4 | UVs y mapas | Inspección UV + bake sin artefactos | P |
| blender-lighting | EX-04 lookdev | Render de revisión (42.2) | Setup neutro + escena | Render comparativo | P |
| blender-cameras | EX-04 lookdev, 58 storyboard | Vistas frontal/lateral/¾ de revisión | Cámaras de revisión | Renders V0–V2 | P |
| blender-rendering | EX-04 | Capturas de aceptación (45.3) | PNG en `SourceArt/_evidence` | Archivos reales | P |
| blender-animation | EX-04/06 · CHR/BOT/entorno | Clips de 49/60 | Acciones nombradas, bake | Rango/nombres verificados en Unity | P |
| blender-export | EX-00 (probe) → todos | Export FBX 24.2 | FBX en `Assets/_Game/Art/Models` | Import Unity sin warnings críticos | A (probe) |
| animation-quality-gate | EX-04/06 | Tras clips de bots/Esneider | Contact sheet + veredicto | Informe por clip | P |
| quality-refinement-autoloop | EX-04+ | Gate V0–V4 fallido | Diagnóstico y corrección | Registro de reintento | P |
| reference-to-3d, orthographic-registration, multiview-constraint-solver, multiview-fit-loop, landmark-fit-repair, fit-repair-optimizer, reference-analysis-validator, reference-look-calibration | EX-04 | Solo cuando existan hojas VIS/REF ortográficas (82) | Modelo source-locked | Overlays/IoU | P (bloqueadas por VIS pendientes) |
| wireframe-to-3d, contour-to-mesh, source-part-segmentation | EX-04 | Solo con planos/wireframes PNG de un asset | Malla desde contorno | Validación silueta | P (condicional) |
| atlas-uv-fitting, texture-driven-mesh-fitting, closed-surface-uv-coverage | EX-06 · kit/trims | Atlas o trim sheet del kit modular (22.1) | UV por región | Cobertura de caras cerradas | P (condicional) |
| texture-state-animation | EX-06 · consolas/monitores | Estados de pantalla (OBJ-003/045/074) | Plan de estados sin crossfade | Verificado en Unity | P (condicional) |
| orbital-hud-motion | — | Anillos/HUD decorativos alrededor de logo | — | — | NA: el HUD del juego se hace en Unity UI; no hay motion graphics de logo |
| mascot-logo-reconstruction | — | Reconstrucción 1:1 de mascota/logo | — | — | NA: no hay activo de marca que replicar; el logo de empresa ficticia es placa/decal (OBJ-016) |

## Unity

| Skill | Sistema / contrato del maestro | Condición | Entregable | Evidencia | Estado |
|---|---|---|---|---|---|
| unity-foundations, unity-scripting, unity-lifecycle, unity-3d-math, unity-async-patterns | 20 arquitectura, todo C# | Desde EX-01 | Scripts en `Assets/_Game/Scripts` | Compila sin errores, tests | P |
| unity-game-architecture, unity-data-driven | 20.1, 95 datos centralizados | EX-01 | Servicios + ScriptableObjects de datos | Validadores 95.2 | P |
| unity-game-loop, unity-state-machines | GameFlow 20.1, 78 FSM | EX-02 | GameFlowController, EnemyBrain | QA-01..04 | P |
| unity-input, unity-input-correctness | 9 controles, 81.3 | EX-02 | Input Actions | Demostración de controles | P |
| unity-physics, unity-physics-queries | 20.2/20.3, 84, 96 | EX-02 | CharacterController, props Rigidbody, capas | QA-05/12/19 | P |
| unity-ai-navigation, unity-npc-behavior | 14, 77, 78 | EX-02 | NavMesh + percepción | QA-13 | P |
| unity-animation | 21, 49, 86 | EX-04 | Animator, transiciones con commit | Video cancelaciones | P |
| unity-cinemachine | 9 cámara, 58 apertura | EX-02/05 | Cámara FP, apertura | Sin clipping | P |
| unity-audio | 17, 50, 65.2 | EX-05 | AudioMixer, zonas reverb | Prueba auriculares | P |
| unity-ui, unity-ui-patterns | 18, 81 | EX-02/07 | HUD UI Toolkit | Foco/estados | P |
| unity-save-system, unity-scene-assets | 19, 88, 89 | EX-03 | CheckpointService, regiones aditivas | QA-09/10/11 | P |
| unity-level-design, unity-procedural-gen | 68, 93 eventos | EX-01/06 | Triggers, flags | Reentrada sin repetición | P (procgen: solo variación de set dressing si se pide) |
| unity-graphics, unity-lighting-vfx | 42, 71 URP | EX-04/05 | Materiales URP, luz baked + linterna | Capturas neutra/juego | P |
| unity-performance, unity-platforms | 27, 91.4, 105.2 | EX-05/08 | Profiler, build Win x64 | Mediciones reales | P |
| unity-testing | 28 | EX-02+ | Tests Edit/Play | Resultados | P |
| unity-editor-tools | 68 planos, 66 registro | EX-01 | Gizmos/ventanas de autoría | — | P |
| unity-packages-services | 71.2 | EX-00 | Manifest congelado | `TECH-BASELINE.md` | A |
| unity-2d | — | — | — | — | NA: juego 3D primera persona |
| unity-xr | — | — | — | — | NA: sin VR/AR (102.1 extensiones no encargadas) |
| unity-multiplayer | — | — | — | — | NA: single-player |
| unity-ecs-dots | — | — | — | — | NA: ≤6 unidades activas (27); sin justificación de ECS |

## Negocio

| Skill | Estado |
|---|---|
| economista, emprendedor, financiero-senior, inversionista | NA salvo encargo explícito de viabilidad/presupuesto (instrucción inicial, punto 2). La economía interna del juego sigue 80/103. |
