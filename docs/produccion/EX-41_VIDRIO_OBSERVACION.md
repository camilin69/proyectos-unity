# EX-41 · Vidrio de observación

OBJ-060 sustituye el bloque opaco M060 de REG-S3 por dos módulos de cuatro metros a escala original. Estado integrado, aceptación final pendiente.

## Modelo y montaje

Cada módulo mide 4 × 2.5 m y 0.166 m de fondo máximo con tornillos; contiene 924/1000 triángulos, marco estructural, retenedores, sellos continuos en ambas caras y paño cerrado de 24 mm. Dos mallas/materiales: marco opaco y vidrio transparente. Atlas PBR 512 del marco más máscara RGBA 512 del cristal; el atlas del marco todavía no está compartido con otros objetos.

Fuentes reproducibles: `SourceArt/Scripts/build_observation_glass_ex41.py` y `prepare_observation_glass_ex41.py`. Blender conserva escenas previas y empaqueta mapas. El material fuente usa transmisión; Unity usa URP Lit con alpha y reflexión, sin refracción ni cámaras adicionales. La condensación de bordes y una huella tenue están combinadas en la textura del vidrio, sin planos transparentes superpuestos. El volumen cerrado usa culling posterior para que solo se dibuje la cara exterior visible.

M060 conserva centro de colisión `(235.5,-6.75,50.2)`, ancho 8 m, altura 2.5 m y base a cota -8. El bloque anterior queda desactivado. Cada módulo tiene un BoxCollider sólido WorldStatic, sin trigger ni rotura. RegionSceneBuilder reproduce el montaje mediante ObservationGlassReview.

## Evidencia

114/114 Edit Mode, job `ab83e7f5c4544381a7a757214111327e`, 3.90035 s. Verifica presupuesto, grosor, material, montaje, continuidad y bloqueo por las máscaras de ataque/visión desde ambos lados.

1/1 Play Mode específico, job `1d4563ecf7734ed4b43b50d92d697dc6`, 1.8338743 s. Dispara Net, Bolt y BossBolt desde ambas caras y exige que se detengan antes de cruzar. No equivale a un recorrido completo de combate.

XML y capturas Unity frontal de prefab y vistas regionales sur/norte en `SourceArt/_evidence/EX-41/`. La sala del otro lado se ve; no se observó sorting incorrecto en estas vistas estáticas. No se declara validado todo ángulo, movimiento o hardware.

Build Windows EX41-Observation: Succeeded, 449.34 MB, 68.52 s, cero errores y 55 advertencias. Recibo en `evidencia/build_EX41-Observation.json`; mensajes en `SourceArt/_evidence/EX-41/build_warnings.txt`. Incluyen APIs obsoletas de Unity y falta de RuntimePipelineConfig. La recompilación no demuestra un recorrido jugable completo. Reaplicar el montaje no modifica la escena.

## Pendiente

Composición final de observación y sujetos HUM, remates arquitectónicos del paño (actualmente partición de 2.5 m con espacio hasta techo), atenuación acústica, impactos autorados, consolidación de atlas compartido y recorrido con iluminación final. Esta entrega no instala la ventana narrativa de C-02 ni sustituye sus sujetos ambientales. Mantener aceptación falsa hasta resolver esas relaciones.
