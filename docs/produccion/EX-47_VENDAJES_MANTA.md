# EX-47 · Vendajes y manta

OBJ-054_VendajesManta reemplaza el plano rígido de la camilla M041. Es una malla cerrada de 1.56 × 1 m, con 11 mm de espesor, bordes caídos y perfiles separados para torso, muslos y pies. Tiene 1696 triángulos, dos huesos, un atlas PBR 1K y ningún collider.

La manta cubre el cuerpo hasta el torso, mantiene visibles cabeza, mano y parte de los pies y no oculta la anatomía para corregir errores. El perfil se corrigió tras la primera captura de Unity porque muslos y pantorrillas atravesaban la tela. Los vendajes complementarios de HUM-03 son cuatro capas independientes en antebrazo y tobillo.

El hueso superior desplaza 2.4 mm la región del torso durante un loop de cinco segundos. AmbientLoopPhase usa la misma fase 0.17 que HUM-01, de modo que cuerpo y tela respiran juntos sin cloth simulation.

## Verificación

- 123/123 pruebas Edit Mode: dimensiones, presupuesto, pesos, ejes, deformación superior a 2 mm, ausencia de collider y sustitución del plano antiguo.
- Captura de Unity revisada tras elevar los perfiles de piernas y pies.
- Hoja de contacto de cuatro tiempos sin alertas automáticas.

Fuente reproducible: `SourceArt/Scripts/build_blanket_ex47.py`. Evidencia y XML en `SourceArt/_evidence/EX-47/`.

## Pendiente

Refinar pliegues secundarios y costura perimetral, añadir roce de tela y revisar con la linterna de juego. Estado Integrado, `acceptance_proven=false`.
