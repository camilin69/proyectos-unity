# Informe QA (EX-08 · 91.3 FIN-01…13) · 2026-09-18

Hardware de medición: Intel Core i5-7500 @ 3.40 GHz · Intel HD Graphics 630 (D3D11) · 24 GB · Windows 10 Pro 19045. Build Release Windows x64 `0.1.0` (`evidencia/build_Release.json`, commit de referencia en el JSON), 1280×720 ventana, vsync 0, calidad "PC", perfil local 720p/30 (71.3). No se midió en el equipo destino de 105 (no disponible): compatibilidad con equipo distinto **no verificada**.

## Pruebas automáticas

| Suite | Resultado | Evidencia |
|---|---|---|
| EditMode (`Esneider.Tests.EditMode`): contratos de núcleo, guardado robusto (truncado, checksum, versión futura, temporal huérfano, rotación), economía 80.1 | 23/23 | `evidencia/tests_EditMode.md` |
| PlayMode (`Esneider.Tests.PlayMode`): sandbox QA-01…08, IA del Vigía, persistencia QA-09…11, streaming, narrativa EVT-01/C1, sectores (patrullas/mobiliario/EVT-16/18/C2), jefe, menús, recorrido completo O01→O11 | 30/30 | `evidencia/tests_PlayMode.md` (07:46) |

## Gates FIN

| Gate | Resultado | Evidencia / notas |
|---|---|---|
| FIN-01 campaña | **Pasa (registro automático)** | `CampaignRunPlayTests.MainRoute_EndToEnd`: O01–O11, cuatro sectores, tres armas, jefe, panel final, D29, ESCAPE y SAVE-END; sin documentos obligatorios. Sin vídeo de partida manual completa. |
| FIN-02 alternativas | **Parcial** | Rutas opcionales (jaulas B, oficina, piezas) y unidades evitables están cableadas (77.1/79.1); el jefe es vencible solo con varilla (60 golpes × 20) por diseño; no existe prueba automática de sigilo completo. |
| FIN-03 daño/balance | **Pasa** | QA-01 (3/6 golpes), QA-02 (rayos 90/60/30/0), jefe 1200 HP con umbrales 800/400 (`BossPlayTests`), commits de recarga 86.3/86.4 (QA-06). |
| FIN-04 persistencia | **Pasa** | Snapshots CP-00…CP-07 y SAVE-END en el recorrido; QA-09/10/11; CP-06 idempotente (max, no suma); muertos/puertas/pickups/carros por GUID. |
| FIN-05 streaming | **Pasa** | `StreamingPlayTests` (precarga por permiso, liberación al avanzar, reentrada sin duplicación); corrección OP-0068 del teletransporte. Sesión de 30 min: ver abajo. |
| FIN-06 recuperación | **Pasa** | `SaveStoreTests`: truncado, checksum, rechazos semánticos, versión futura preservada, temporal huérfano; recuperación de backup en Play (QA-11). Pendientes de 89.5: GUID duplicado y espacio insuficiente sin prueba inyectada. |
| FIN-07 arte | **Mejorado y medido; revisión humana pendiente** | Los 16 assets se refabricaron con detalle mecánico real: 58 304 → 148 326 tris (×2.5) y todos los hero dentro del presupuesto 43 por primera vez; el detalle del normal map sube de 0.2–3.3° a 3–22° de desviación media (la medida que probaba que antes estaban planos). El material incorpora bevel, desgaste por pointiness y AO de cavidad, que sí se hornean. Sigue **sin** escultura high→low ni texturizado pintado con intención, y los robots necesitan 2K de textura para resolver el detalle nuevo. Evidencia: `_evidence/EX-04/*` y `EX-09_showcase_tierA.png`. |
| FIN-08 animación | **Parcial, ahora con evidencia numérica** | `SourceArt/Scripts/measure_contacts.py` mide cada clip frame a frame contra umbrales escritos y emite `_evidence/EX-08/contacts_*.json`. Corregido: los clips de muerte enterraban el cuerpo (Vigía 361 mm, Custodio 600, Archivista 876) y el arma colgaba de la cámara en vez de la mano. Abierto y medido: pie flotando en los ciclos de marcha (fracción de apoyo 0.52–0.62 contra 0.85) y dispersión de velocidad del pie apoyado hasta 88 %. |
| FIN-09 sonido | **Pasa (síntesis declarada)** | 91 WAV originales con ficha (`AUDIO_MANIFEST.json`), PA localizada en OBJ-065 con alerta y voz filtrada, telegraphs sonoros del jefe; sin licencias de terceros. |
| FIN-10 interfaz | **Pasa** | Menús navegables con teclado y foco visible, texto 150 % (`EX-08_ui_pause_text150.png`), mapa (`EX-08_ui_map.png`), ajustes persistentes (`EX-08_ui_settings.png`, `MenuPlayTests`), documentos (`EX-08_ui_documents.png`). Sin vídeo. |
| FIN-11 rendimiento | **Pasa (perfil local 720p/30)** | Tabla siguiente. |
| FIN-12 taller | **Preparado** | `MATRIZ_TALLER.md` con evidencia por requisito; aceptación de modelos propios como "externos" pendiente del docente. |
| FIN-13 paquete | **Parcial** | Proyecto completo en el repositorio + README/controles/créditos/licencias; build reproducible desde el editor. No se probó abrir desde una copia comprimida independiente. |

## FIN-11 · seis tramos 91.4 (Release, 60 s tras 2 s de warmup, ruta automática, mundo simulando)

| Tramo | Mediana (ms) | p95 (ms) | FPS mediana | Hitches >100 ms | Excepciones en log | Notas |
|---|---|---|---|---|---|---|
| S1 apertura (P01) | 15.0 | 16.8 | 67 | 0 | 0 | `perf_Release_S1_apertura.json` |
| S2 nave (P03) | 19.2 | 24.9 | 52 | 1 | 0 | patrullas V02/V03/K01/K02 activas y disparando |
| S3 jaulas A (P05) | 16.7 | 21.4 | 60 | 1 | 0 | 8 conjuntos de barrotes |
| S3 clínica (P05) | 16.9 | 21.8 | 59 | 0 | 0 | |
| S4 control (P06) | 16.0 | 18.2 | 63 | 0 | 0 | |
| S4 jefe fase III (arena) | 16.5 | 19.6 | 61 | 0 | 0 | combate real (jefe a 300 HP, `combat: true`) |

Criterio 91.4: mediana ≤ 33.3 ms y p95 ≤ 40 ms por tramo → **cumplido en los seis**; hitches aislados (1 en S2 y S3-A: precarga de región vecina) registrados sin borrarlos.

Dos tandas previas se descartaron por inválidas y quedan registradas (OP-0070/OP-0074): (1) el menú de Inicio abierto congelaba la simulación en la build sin operador; (2) **defecto S1 en build**: `Shader.Find` devolvía null por stripping y `Projectile.Create` lanzaba una excepción por frame (392 211 en 30 min) — en la build los bots nunca disparaban y la memoria crecía ~30 MB por carga por los primitivos huérfanos. Corregido con materiales como assets en `Resources/Materials` y fallback funcional sin material; verificado con 0 excepciones en los seis logs `player_Release_*.log`.

Sesión de 30 min con 24 cambios regionales (`-perfsession 30`, `perf_Release_session.json`): mediana 14.2 ms, p95 22.6 ms, 2 hitches, 0 excepciones. Memoria asignada al volver al mismo contexto: 241.3 MB (t=75 s) → 264.2 MB (t=975 s) → 266.8 MB (t=1801 s); +9.5 % respecto a la primera muestra (tomada antes de cargar cada región una vez) y **+0.9 % entre retornos posteriores** → sin crecimiento continuo (criterio 91.4: investigar > 10 %). Reservada 538.6 → 542.6 MB. La primera sesión (build defectuosa) había mostrado +291 %.

## Defectos abiertos y limitaciones

1. Arte: sin escultura high→low ni texturizado pintado con intención (sigue siendo procedural, aunque ya no es blockout). Los robots necesitan textura de 2K para resolver el detalle añadido: a 1024 el atlas empaqueta el doble de islas y el texel density cae. Archivista a 34 600 tris, justo por debajo del mínimo de su rango. Cuatro props entre 3.1k y 4.1k, por encima del techo de 3k. Kit de mobiliario sin materiales/LOD; vidrio M060 opaco; hojas VIS de 82 pendientes (HUM).
2. Animación: los ciclos de marcha mantienen la pelvis a altura constante mientras las piernas rotan, así que el pie flota (fracción de apoyo Custodio 0.52, Archivista 0.62 contra el mínimo 0.85) y su velocidad durante el apoyo varía hasta un 88 %. Residuo de penetración de 7–17 mm en los ciclos, porque no keyean el hueso raíz. Giro de cabeza en patrulla (77.1) sin implementar; gesto de huella en la criocámara (PIL-02) no implementado (abre por clip en EVT-01).
3. Física: PIL-08 cerrado (`WorldPhysicsPlayTests` 5/5). Abierto: la varilla y los disparos no producen reacción sobre los props (84.2 RX-2), y una puerta puede cerrarse atravesando el carro.
4. Señalética 87.1/87.2 (NAV-01…07) no fabricada; el mapa cubre la orientación.
5. Interfaz en uGUI (81 recomienda UI Toolkit); mando no soportado; volúmenes por grupo no expuestos (solo maestro).
6. Rendimiento: medido solo en el equipo de desarrollo (perfil local); 1080p/60 no evaluado; build Development con profiler generada pero sin captura de profiler adjunta.
7. Datos: velocidades del jugador (9) marcadas VAL; métricas de gasto por tramo (80.3) sin jugadores.
8. Técnica: GPU Resident Drawer desactivado por crash (OP-0067); audio WAV en git sin LFS (131 MB).
9. Persistencia: pruebas de GUID duplicado y espacio insuficiente (89.5) no inyectadas; cierre durante escritura cubierto solo por truncado.
