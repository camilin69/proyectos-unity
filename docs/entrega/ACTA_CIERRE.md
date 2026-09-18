# Acta de cierre (91.6) · candidato 0.1.0 · 2026-09-18

**Estado: candidato técnico presentado; la decisión humana de cierre está pendiente (106.3).** Aprobar este documento no aprueba la build. Reabrir cualquier gate si cambia rig, pipeline, escena, versión de guardado, ataque o fuente de asset que afecte su evidencia.

## Alcance probado

Campaña completa S1→C1→S2→C2→S3→C3→S4→exterior con tres armas, linterna, 23 Vigías / 14 Custodios / 1 Archivista según catálogo 68, checkpoints CP-00…CP-07 y SAVE-END, menús, mapa y ajustes; medido en build Release Windows x64 en i5-7500 / HD 630 (perfil local 720p/30).

## Gates

| Gate | Resultado | Evidencia |
|---|---|---|
| FIN-01 campaña | Pasa (registro automático) | `evidencia/tests_PlayMode.md` (CampaignRun) |
| FIN-02 alternativas | Parcial | 77.1/79.1 cableados; sin prueba de sigilo |
| FIN-03 daño/balance | Pasa | Sandbox QA, `BossPlayTests`, `EconomyTests` |
| FIN-04 persistencia | Pasa | Persistence/Campaign tests |
| FIN-05 streaming | Pasa | `StreamingPlayTests`; sesión 30 min / 24 cambios: mediana 14.2 ms, p95 22.6, 2 hitches, memoria 241 → 264 → 267 MB (+0.9 % entre retornos tras la meseta), 0 excepciones (`perf_Release_session.json`) |
| FIN-06 recuperación | Pasa (con 2 casos de 89.5 no inyectados) | `SaveStoreTests` |
| FIN-07 arte | Revisar | hojas EX-04, capturas EX-06 |
| FIN-08 animación | Parcial | clips por asset; sin vídeo de contactos |
| FIN-09 sonido | Pasa (síntesis declarada) | `AUDIO_MANIFEST.json` |
| FIN-10 interfaz | Pasa | `EX-08_ui_*.png`, `MenuPlayTests` |
| FIN-11 rendimiento | Pasa (perfil local) | `perf_Release_*.json` |
| FIN-12 taller | Preparado | `MATRIZ_TALLER.md` |
| FIN-13 paquete | Parcial | `README.md`, `LICENCIAS.md`, build regenerable; copia independiente no probada |

## Defectos abiertos

Ver `QA_REPORT.md` (9 grupos abiertos). Un defecto **S1 de build** se detectó y corrigió durante EX-08 (OP-0073/0074): los proyectiles no se creaban en la build por stripping de shaders (los bots no atacaban) y fugaban memoria; tras la corrección los seis logs `player_Release_*.log` no contienen excepciones. Los dos crashes observados fueron del **editor** durante pruebas y quedaron corregidos (OP-0067). No queda ningún S1 conocido (bloqueo de progreso, pérdida de guardado o crash en build).

## Decisiones que corresponden al usuario

1. Publicar/entregar (Drive/Moodle) y confirmar con el docente la aceptación de modelos propios de Blender como "modelos externos".
2. Aceptar el estado artístico "Revisar" como entrega académica o encargar iteración Tier A (33–41) antes del cierre.
3. Mantener P2 como objetivo o activar P1 (102.2).
4. Aceptar la desactivación del GPU Resident Drawer y el HUD en uGUI como decisiones técnicas del candidato.

Decisión de cierre: **No ejecutado (pendiente del usuario)**.
