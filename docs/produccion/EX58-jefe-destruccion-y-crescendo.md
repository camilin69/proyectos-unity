# EX58 — Jefe orientado, destrucción robótica y crescendo musical

## Orientación del Archivista

El modelo del Archivista comparte el contrato visual de los otros robots: su cara importada apunta a -Z y su raíz de juego ataca hacia +Z. `EnemyAnimator.AlignVisualFacing` aplica los 180° también al jefe. `BossBrain` desactiva el giro autónomo del NavMeshAgent fuera de persecución, gira hacia Esneider durante todas las preparaciones —incluido el pulso— y exige una alineación máxima de unos 15° antes de emitir. `Emit` vuelve a comprobar esa condición, por lo que un ataque invocado mientras está de espaldas no produce daño ni proyectil.

## Destrucción de robots

Vigía, Custodio y Archivista usan `RobotDestruction`. Al morir, la carcasa original y sus colliders se ocultan, se separan las mallas principales en fragmentos, aparecen destello y chispas, y las piezas salen despedidas, rebotan contra cobertura y desaparecen gradualmente. El Archivista genera una explosión mayor. El audio `RobotExplosion.wav` fue sintetizado para el proyecto y no usa muestras externas.

El objeto lógico persiste para checkpoints. Cargar un estado donde el robot ya murió lo oculta sin repetir la explosión; cargar un checkpoint anterior elimina los fragmentos, restaura modelo/colliders y permite volver a derrotarlo. Se redujo el número de piezas simultáneas tras la revisión visual para mantener el efecto sin castigar el rendimiento.

## Música por progresión

`ProgressionMusic` mezcla cinco bucles originales sintetizados. El nivel inicial entra después del despertar y aumenta al avanzar por regiones y al abrir D06, D14 y D22/D27. La arena del Archivista usa el quinto nivel. Los hitos de puerta se guardan como flags, así que volver atrás o reabrir una puerta no reduce ni acumula incorrectamente la intensidad.

Al concederse `BOSS_DEFEATED`, las dos fuentes musicales se detienen inmediatamente. Los ambientes regionales continúan y cambian al banco de S1, que contiene aire, viento industrial y goteras del despertar. Cargar un checkpoint anterior restaura el nivel musical correspondiente; una partida nueva vuelve al silencio previo al despertar.

## Validación

- EditMode: 4/4, job `67bde3737ab946a6b2703d161810c9fb`. Orientación animada de Vigía, Custodio y Archivista, además de integridad de los 45 robots de campaña.
- PlayMode dirigido: 5/5, job `47c116aead47471caf724831b18c0ccc`. Bloqueo de ataque posterior del jefe, cara visual, explosión/reaparición de ambos robots normales, progreso musical, silencio final y muerte/reintento del jefe.
- PlayMode completo del jefe: 3/3, job `18d0799a7fbc4f69906df5a4f9a9ff7f`. Tres fases, ataques, restricciones, muerte, CP-07 y restauración desde CP-06.
- Captura de explosión: `EsneiderProtocoloLazaro/Captures/EX58/custodio-explosion-1.png`.
- Durante la apertura de Unity apareció una recuperación de escena de la sesión anterior. Se eligió conservarla en `EsneiderProtocoloLazaro/Assets/_Recovery/0.unity`; no se aplicó ni se eliminó.

Build Windows64 completada: job `build-9d6a5ba78b`, 71,34 s, 226,08 MB, 0 errores y 61 advertencias.

Ejecutable: `Builds/EX58-BossDestructionMusic/EsneiderProtocoloLazaro.exe`.
