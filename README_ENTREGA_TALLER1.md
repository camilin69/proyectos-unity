# ESNEIDER: Protocolo Lazaro - Taller 1 de Unity 2026

## Abrir y ejecutar el proyecto en Unity

1. Instale Unity Hub y Unity `6000.6.1f1`.
2. En Unity Hub seleccione `Add` o `Agregar proyecto desde disco`.
3. Seleccione la carpeta `EsneiderProtocoloLazaro` extraida.
4. Espere a que Unity regenere la carpeta `Library` e importe los assets. El primer inicio puede tardar varios minutos.
5. Abra `Assets/_Game/Scenes/BOOT.unity`.
6. Pulse Play.

Si Unity solicita instalar paquetes, permita que los restaure desde `Packages/manifest.json`. MCP for Unity es una herramienta opcional de desarrollo y no es necesaria para ejecutar el juego.

El paquete omite `Library`, `Temp`, caches y compilaciones anteriores para reducir el peso. Unity reconstruira automaticamente esos archivos al abrirlo por primera vez.

## Gameplay incluido

El video de demostracion se encuentra en `Gameplay/gameplay.mkv`.

## Objetivo

Esneider despierta tras 2000 anos de criopreservacion en el bunker NEMESIS. Debe recorrer sus sectores, conseguir equipo, sobrevivir a los robots, derrotar al Archivista y activar la salida exterior.

## Controles

| Accion | Control |
|---|---|
| Moverse | WASD |
| Mirar | Raton |
| Correr sin limite | Shift |
| Agacharse / saltar | Ctrl / Espacio |
| Interactuar | E |
| Usar arma u objeto de la mano derecha | Clic izquierdo |
| Encender o apagar la linterna de la mano izquierda | Clic derecho |
| Seleccionar inventario | Teclas 1-9 o rueda del raton |
| Recargar | R |
| Curarse | Q |
| Pausa, mapa, documentos y ajustes | Esc |
| Omitir introduccion | E o Espacio |

## Requisitos demostrados

- Escenario tridimensional organizado en regiones y corredores.
- Movimiento e interaccion mediante teclado y raton.
- Rigidbody funcional en carros desplazables.
- Colisiones detectadas por codigo con consecuencias de ruido e impactos.
- Triggers para checkpoints, regiones, eventos y finalizacion.
- Variables configurables desde el Inspector mediante ScriptableObjects y componentes.
- Modificacion de luces, colliders, objetos y otros componentes por codigo.
- Camara coherente en primera persona.
- Mas de diez materiales, texturas PBR y Physic Materials observables.
- Dieciseis modelos originales creados en Blender e importados en Unity como FBX.
- Condiciones de derrota, captura y victoria con estadisticas finales.

## Modelos y licencias

Los modelos 3D son originales del proyecto y fueron creados en Blender. No se descargaron modelos de Sketchfab ni de otras bibliotecas, por lo que no existen enlaces externos de descarga. Los FBX evaluables estan incluidos en `Assets/_Game/Art/Models` y la procedencia completa se encuentra en `Documentacion/LICENCIAS.md`.

## Estructura del paquete

- `EsneiderProtocoloLazaro`: proyecto completo de Unity.
- `Gameplay/gameplay.mkv`: video de demostracion del juego.
- `docs/entrega`: descripcion, matriz de requisitos, informe QA y licencias.

No se incluyen `Library`, `Temp`, `Logs`, `obj` ni `UserSettings`; Unity los regenera automaticamente y no forman parte del proyecto fuente necesario.

## Integrantes

- Camilo Antonio Merchan Santos - 202220095
