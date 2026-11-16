# Sueño Lúcido — Taller Final (Electiva IV, UPTC)

Un viaje por ocho sueños entre el amanecer y la medianoche. Una figura de tela sin rostro despierta en un cuarto
de azulejo rosa y menta; en cada sueño hay un recuerdo escondido que abre el paso al siguiente. El cielo cambia
con el viaje: las 07:00 en el cuarto, el mediodía en la colina del árbol, la noche estrellada en el jardín
inundado, y la medianoche en lo alto de una escalera de moqueta rosa que devuelve al mismo cuarto.

## Cómo jugar
1. Abrir `SuenoLucido.exe` (o en Unity, la escena `Assets/_Project/Scenes/Boot.unity` y Play).
2. En la pantalla inicial elegir **Calidad: Cine** (GPU dedicada) o **Ligero** y pulsar **DORMIR** o Enter.
3. Controles: WASD caminar · Shift trotar · Espacio saltar · Ratón mirar · E recordar · Q volar (solo en el cielo)
   · F cámara de cine (3 ángulos y vuelta a primera persona) · Tab saltar cinemática · Esc pausa.

## Los ocho sueños
| # | Escenario | Hora | Paso al siguiente |
|---|---|---|---|
| 1 | El cuarto | 07:00 | La puerta de luz (el sol entra por la ventana en un haz con polvo) |
| 2 | La pradera | 09:00 | La puerta que da a otro cielo: el viento lo levanta |
| 3 | La colina del árbol | 12:00 | Vuelo corto entre nubes; el hueco tallado del árbol (salto a las 20:00) |
| 4 | El vestíbulo inundado y el jardín | 20:00 | Bajo el cometa, el túnel junto al último nenúfar |
| 5 | El pasillo de las ondas | 20:40 | Abajo se bifurca: la luz a la derecha; a la izquierda, el hueco con la luna y la fuente del ángel |
| 6 | La playa infinita | 21:20 | Palmeras altísimas, el laberinto que oscurece y el túnel con luz |
| 7 | La piscina liminal | 22:40 | La pasarela sobre agua sin fondo y la puerta en la pared de cielo pintado |
| 8 | La escalera al cielo | 23:30 | Antorchas y un meteorito que se acerca; al tomar el último recuerdo cae y la tierra tiembla: de vuelta al cuarto, 00:00 |

Al final, **Seguir soñando** deja recorrer el cuarto a las 3:33 para siempre: oscuro, con la luna llena enorme
en la ventana, el cielo rosado y nubes de algodón; sin puertas ni recuerdos.

## Cómo está hecho
- **Todo se genera desde código**: *Sueño Lúcido → Construir viaje completo* reconstruye el Animator desde
  `PlayerAnimatorSpec.json`, el Boot y los 8 escenarios (`Assets/_Project/Editor/Build/`).
- El diagrama del Animator (`Docs/Diagrama_Animator.png`) sale de la misma spec; una prueba exige que el
  controller real coincida.
- Escenas aditivas: `Boot` vive todo el viaje; cada escenario entra mientras una cinemática tapa la carga.
- Música: `python tools/taller_final/audio_loop.py cancion.mp3` deja el bucle sin costura en
  `Assets/_Project/Audio/Music/` (fuera del repositorio por derechos) y se reconstruye el viaje.
