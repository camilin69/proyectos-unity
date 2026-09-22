# ESNEIDER: Protocolo Lázaro

Proyecto realizado por **Camilo Antonio Merchan Santos — 202220095** para el Taller 1 de Unity 2026.

Es un juego de terror y acción en primera persona. Esneider despierta después de 2000 años de criopreservación dentro del búnker NEMESIS. El jugador debe explorar sus sectores, reunir equipo, enfrentarse a los robots, derrotar al Archivista y encontrar la salida.

## Requisitos

- Windows 10 u 11 de 64 bits.
- [Git](https://git-scm.com/download/win).
- [Unity Hub](https://unity.com/download).
- Unity **6000.6.1f1** con el módulo **Windows Build Support (IL2CPP)** si se desea generar un ejecutable.
- Conexión a Internet durante la primera apertura para restaurar los paquetes declarados en `Packages/manifest.json`.

No es necesario descargar `Library`, `Temp`, `Logs`, `obj`, builds ni otros archivos generados. Unity los reconstruye localmente.

## Clonar y jugar desde Unity

1. Clonar el repositorio:

   ```powershell
   git clone https://github.com/camilin69/proyectos-unity.git
   ```

2. Abrir **Unity Hub** y elegir **Add > Add project from disk**.
3. Seleccionar la carpeta `proyectos-unity/EsneiderProtocoloLazaro`.
4. Confirmar la versión **Unity 6000.6.1f1**.
5. Esperar a que Unity descargue los paquetes y regenere la carpeta `Library`. La primera importación puede tardar varios minutos.
6. Abrir `Assets/_Game/Scenes/BOOT.unity`.
7. Pulsar **Play**.

## Construir el ejecutable para Windows

1. Abrir el proyecto y esperar a que termine de importar sin errores.
2. Ir a **File > Build Profiles**.
3. Seleccionar **Windows** y la arquitectura **Intel 64-bit**.
4. Verificar que `Assets/_Game/Scenes/BOOT.unity` sea la primera escena habilitada. Las escenas de las regiones ya están declaradas en `ProjectSettings/EditorBuildSettings.asset`.
5. Pulsar **Build**, crear una carpeta fuera del repositorio, por ejemplo `EsneiderBuild`, y esperar a que Unity termine.
6. Ejecutar `EsneiderProtocoloLazaro.exe` desde la carpeta generada.

## Controles

| Acción | Control |
|---|---|
| Moverse | WASD |
| Mirar | Ratón |
| Correr sin límite | Shift |
| Agacharse / saltar | Ctrl / Espacio |
| Interactuar | E |
| Usar arma u objeto de la mano derecha | Clic izquierdo |
| Encender o apagar la linterna izquierda | Clic derecho |
| Seleccionar inventario | Teclas 1–9 o rueda del ratón |
| Recargar | R |
| Curarse | Q |
| Pausa, documentos y ajustes | Esc |
| Omitir introducción | E o Espacio |

## Contenido evaluable

- Escenario tridimensional dividido en regiones y corredores.
- Movimiento, interacción, inventario de nueve espacios y combate en primera persona.
- Rigidbody, colisiones, triggers, checkpoints y restauración del estado del mundo.
- Enemigos con navegación, percepción, combate, animaciones y destrucción.
- Iluminación ambiental, linterna, efectos visuales y música dinámica en crescendo.
- Más de diez materiales y texturas PBR.
- Modelos originales realizados en Blender e importados como FBX.
- Condiciones de derrota y victoria con enfrentamiento final.

Los modelos FBX necesarios para ejecutar el juego están en `EsneiderProtocoloLazaro/Assets/_Game/Art/Models`. La documentación de la entrega y las licencias se encuentra en [`docs/entrega`](docs/entrega).

## Solución de problemas

- Si Unity solicita restaurar paquetes, aceptar y esperar a que finalice.
- Si el proyecto se abrió con otra versión, cerrarlo e instalar exactamente `6000.6.1f1` desde Unity Hub.
- Si la escena no inicia automáticamente, abrir `Assets/_Game/Scenes/BOOT.unity` antes de pulsar Play.
- Si Git muestra rutas demasiado largas en Windows, ejecutar una vez `git config --global core.longpaths true` y volver a clonar.
