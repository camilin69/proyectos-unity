# Mantenimiento Racing — especificación de requisitos v1.0

- **Estado:** especificación para revisión; esta rama contiene planeación, no un juego implementado.
- **Producto:** carreras arcade multijugador en un circuito industrial 3D.
- **Primera entrega jugable:** un mapa, tres familias de vehículos, carreras de 2 a 8 personas y poderes recogidos en pista.
- **Control decisivo:** `F` activa el poder equipado; acelerar, frenar y derrapar tienen teclas independientes.
**Referencia de género:** la lectura inmediata de la carrera, las vueltas, el derrape y la sorpresa de los objetos de Mario Kart 64. Vehículos, pista, iconos, personajes, música, efectos, interfaz y mallas serán originales de **Mantenimiento Racing**.

---

## 1. Cómo leer y usar este documento

1. Las secciones 2–5 fijan el concepto, alcance y lenguaje visual.
2. Las secciones 6–9 son el contrato espacial del único circuito. **No se modela arte final antes de aprobar la cinta vial, sus límites y una vuelta completa.**
3. Las secciones 10–15 fijan vehículos, controles, carrera, lobby y poderes.
4. Las secciones 16–20 definen sistema técnico, contenido, producción, pruebas y entregables.
5. Todo valor marcado `VAL` es un punto de partida para sesiones de prueba; cambiarlo requiere registrar motivo, versión y resultado. Las coordenadas `GEO` son contractuales hasta aprobar una revisión del circuito.

**Identificadores:** `RF` requisito funcional; `RNF` requisito no funcional; `GEO` geometría; `BAL` balance; `UX` interfaz; `ART` arte; `RED` red; `QA` prueba/aceptación. `P0` bloquea la primera partida completa; `P1` se incluye antes de presentar como versión jugable; `P2` es una extensión. Los criterios de aceptación son condiciones observables, no intenciones.

**Decisión de alcance:** se construye **una sola pista terminada**, con tres sectores memorables, antes de pedir pistas adicionales. Un editor, tiendas, campaña, batalla independiente, inteligencia artificial competitiva y progresión monetizada quedan fuera de v1.

## 2. Objetivo, público y promesa de juego

`RF-001 · P0` Una persona debe poder crear una sala, invitar por código o enlace, escoger vehículo y completar una carrera contra al menos otra persona. El resultado final identifica clasificación, tiempo total, vueltas válidas y penalizaciones.

`RF-002 · P0` La meta es cruzar primero la línea tras **3 vueltas válidas** por defecto; el anfitrión puede configurar 1–5 vueltas. El objetivo debe ser visible antes de empezar y al terminar.

`RF-003 · P0` La carrera combina trazada, derrape, boosts cortos y poderes. Los golpes retrasan temporalmente; no eliminan a nadie de la carrera.

**Pilares:**

1. **La pista es la protagonista.** El jugador anticipa curvas, límites y riesgos sin memorizar trampas invisibles.
2. **Vehículos industrialmente reconocibles.** Izaje, transporte y minas se leen por su silueta a distancia; ninguno obtiene ventaja injusta por tamaño visual.
3. **Arcade controlable.** Un principiante termina una vuelta sin dominar el derrape; un experto gana tiempo con una buena trazada.
4. **Poderes que cambian decisiones, no sustituyen la conducción.** Advertencia, defensa, contrajuego y duración limitada.
5. **Multijugador claro.** Posición, vueltas, objetos, estado de conexión y ganador proceden de una autoridad común.

**Referencias verificadas:** el [manual oficial de Mario Kart 64](https://www.nintendo.com/eu/media/downloads/games_8/emanuals/nintendo_8/Manual_Nintendo64_MarioKart64_EN.pdf) documenta carreras VS de 2–4 participantes, tres vueltas y cajas de objetos; aquí se toma ese vocabulario de diseño y se cambia a una identidad de patio industrial con soporte objetivo para 2–8 personas. No se importan ni recrean recursos de Nintendo.

## 3. Alcance verificable de v1

| Sistema | Incluido en v1 | Fuera de v1 |
|---|---|---|
| Carrera | 2–8 participantes, 1–5 vueltas, cuenta regresiva, clasificación y resultados | Copas, temporadas, torneos |
| Pista | Una pista cerrada con tres sectores, 4 filas de recogida, 2 zonas de boost y recuperación | Atajos secretos y mapas adicionales |
| Vehículos | Tres modelos base originales, uno por área; libreas diferenciadas sin ventaja | Personalización de piezas con estadísticas |
| Objetos | Cinco poderes industriales, un espacio de inventario y activación con F | Tienda y acumulación de objetos |
| Lobby | Sala por código, selección, preparación, anfitrión y reconexión breve | Cuentas y matchmaking público |
| Gráficos/sonido | Estética retro 3D legible, audio espacial y HUD completo | Réplicas de sprites, música o iconos existentes |
| Rendimiento | Perfil objetivo de escritorio; degradación gráfica | Móviles y realidad virtual |

Una sala con un solo jugador puede ejecutar **contrarreloj local de prueba** para verificar pista y controles; no contará como partida multijugador completada. El modo contrarreloj no necesita poderes ni ranking público en v1.

## 4. Dirección de arte original

`ART-001 · P0` Estética 3D arcade inspirada en la economía visual de finales de los 90: siluetas simples pero elaboradas, geometría facetada intencional, texturas pintadas o de baja frecuencia, colores saturados controlados y lectura a larga distancia. **No** reproducir pilotos, karts, bloques de interrogación, conchas, tipografía, patrones de pista ni música reconocibles de Mario Kart.

**Lenguaje propio:** estación industrial de mantenimiento y extracción al atardecer. Asfalto gris azulado, acero oxidado, señalética ámbar, maquinaria turquesa, mineral violeta y cielo cobrizo. Las líneas de seguridad y las balizas marcan límites; el material rugoso y el polvo comunican cambios de agarre.

`ART-002 · P0` En tercera persona, cada vehículo debe distinguirse a **50 m** por contorno: gancho/mástil para izajes, cabina y remolque compacto para transporte, volqueta y tolva para minas. Los remolques y brazos decorativos nunca sobresalen de su collider jugable.

`ART-003 · P1` La pista debe guiar la mirada: grúas amarillas antes del sector de izaje, silo rojo antes del sector minero, pórticos azules de carga en transporte. Las curvas cerradas muestran marcas de frenada y chevrones antes de su punto de giro. Ninguna luz de decoración debe parecer un objeto recogible.

`ART-004 · P1` Los tres sectores conservan la misma lógica de límites: doble línea continua en el borde transitable, franja de grava no competitiva, defensa física visible y un fondo inaccesible. Los cortes de terreno por abajo no se camuflan solo con niebla.

**Catálogo mínimo de materiales:** asfalto, asfalto desgastado, tierra compactada, grava, hormigón, acero pintado, acero oxidado, caucho, mineral, cristal, pintura reflectiva, emisión de baliza y agua somera decorativa. Cada uno tiene albedo/roughness coherentes y versión de baja resolución. El brillo de las cajas de poder usa silueta hexagonal y marca de rayo industrial propia.

**Cámara y claridad:** cámara trasera con campo visual inicial de 70° horizontal; aumento máximo de 6° a alta velocidad, sin oscilaciones que impidan anticipar la curva. Horizonte visible por delante al menos 45 m. Objetos interactivos se diferencian también por forma y animación, no solo color. Reducir destellos en modo accesible.

## 5. Glosario y medidas

- `s`: distancia recorrida sobre la **línea central** de la pista, en metros, medida desde meta y en sentido de carrera.
- `d`: desplazamiento lateral respecto a la línea central; negativo a la izquierda del avance, positivo a la derecha.
- `ancho transitable`: distancia entre las dos líneas interiores de borde; una rueda puede tocar la franja pintada sin sanción.
- `límite duro`: barrera con collider; nunca se usa para ocultar una salida visual de la pista.
- `zona recuperable`: grava/hormigón exterior donde el vehículo puede maniobrar lentamente de vuelta.
- `fuera de pista`: posición que excede el polígono permitido, caída, vuelco irreversible o atasco.
- `checkpoint de vuelta`: plano direccional invisible que valida progreso, distinto de un respawn.
- `punto de rescate`: pose segura precalculada con posición, altura y orientación tangente.
- `poder`: objeto equipado tras recoger un módulo; `F` lo consume.

Unidades de diseño: metros, segundos, km/h solo para HUD; simulación en m/s. Coordenadas del mundo: `X` este, `Z` norte, `Y` arriba. Giro de vuelta en sentido antihorario visto desde arriba.

## 6. Circuito único: **Anillo de la Cantera**

`GEO-001 · P0` Mapa cerrado de **520 × 420 m**: `X ∈ [-260, 260]`, `Z ∈ [-210, 210]`. El circuito enlaza sur (transporte), este (minas), norte/oeste (izajes) y vuelve al sur. La línea central de referencia tiene ≈ **1.357 m** en su polilínea; la longitud de la curva suavizada se mide y congela en el asset de pista antes del arte final. Una vuelta objetivo de prueba dura **95–125 s** sin poderes. Esta duración es `VAL`, no promesa de tiempo exacto.

`GEO-002 · P0` Se genera una cinta vial 3D a partir de los puntos de control siguientes; cada punto mantiene `Y` del perfil altimétrico definido después. Los arcos deben ser tangentes, sin esquina geométrica instantánea. El diseñador puede mover cada punto máximo ±5 m durante la fase de gris para corregir radios; después requiere revisión documentada de todos los checkpoints y filas de objetos.

| Punto | X | Z | s de polilínea aprox. | Sector / intención |
|---|---:|---:|---:|---|
| P00 | -160 | -150 | 0 | Meta y salida, hacia el este |
| P01 | -80 | -150 | 80 | Recta de transporte |
| P02 | 0 | -145 | 160 | Pórtico de tractomulas |
| P03 | 100 | -150 | 260 | Zona de adelantamiento |
| P04 | 175 | -142 | 336 | Cartel de frenada antes de mina |
| P05 | 215 | -110 | 387 | Curva amplia al norte |
| P06 | 220 | -30 | 467 | Ascenso minero |
| P07 | 195 | 20 | 523 | Chicana legible |
| P08 | 215 | 90 | 596 | Tolvas y mineral |
| P09 | 185 | 145 | 658 | Giro al oeste |
| P10 | 100 | 160 | 745 | Recta alta, vista panorámica |
| P11 | 20 | 152 | 825 | Inicio zona de izaje |
| P12 | -50 | 165 | 896 | Grúas de pórtico |
| P13 | -130 | 155 | 977 | Pasarela elevada decorativa |
| P14 | -195 | 130 | 1047 | Curva occidental |
| P15 | -215 | 80 | 1100 | Descenso controlado |
| P16 | -200 | 10 | 1172 | Patio de bobinas |
| P17 | -215 | -55 | 1239 | Regreso a cota baja |
| P18 | -205 | -115 | 1300 | Curva final señalizada |
| P19 | -170 | -145 | 1346 | Entrada a meta |

**Esquema cenital de orientación (no está a escala; manda la tabla de coordenadas):**

```text
                           NORTE (+Z)
                  IZAJES    ← ← ←  MINAS / MESETA
              ┌───────────────────────────────┐
              │                               ↑
    RETORNO   ↓                               ↑  MINAS
              │                               ↑
              └─ META → → TRANSPORTE → → → ───┘
                           SUR (-Z)          ESTE (+X)
```

`GEO-003 · P0` La malla de superficie, las bandas laterales, colliders, minimapa, checkpoints y puntos de respawn se derivan **del mismo spline versionado**. No se mantiene una segunda pista de colisiones dibujada a mano. Resampleo máximo cada 2 m; error entre borde visual y borde de colisión ≤0,25 m en curvas y ≤0,1 m en rectas.

### 6.1 Ancho, radios y pendiente

| Tramo de `s` | Ancho transitable | Restricción | Lectura visual |
|---|---:|---|---|
| 0–335 | 20 m | Recta para hasta tres vehículos en paralelo | Marcas de carril y pórticos |
| 335–660 | 18 m | Minería; chicana P06–P08 sin cuello oculto | Chevrones ámbar y luces de mina |
| 660–1015 | 18 m | Izajes; grúas fuera del borde | Marcas de carga y ganchos elevados |
| 1015–1357 | 19 m | Descenso y retorno | Balizas y barreras continuas |

`GEO-004 · P0` Ancho mínimo **16 m**, incluso en la chicana; ancho libre sobre power-ups ≥15 m. Radios de curva objetivo ≥25 m en giro principal y ≥18 m en chicana, medidos sobre línea central suavizada. Ninguna prop, sombra o estructura cuelga por debajo de 5,5 m de altura útil sobre la calzada. La cámara tiene un corredor libre detrás del vehículo o se acerca automáticamente sin atravesar objetos.

`GEO-005 · P0` Altura `Y`: salida y transporte 0 m; P05 1 m; P06 4 m; P08 9 m; P09–P13 10 m; P14 8 m; P16 3 m; P18 0 m; llegada 0 m. Pendiente longitudinal ≤6 % en superficie jugable, peralte ≤6°. Estos valores se interpolan sin escalones y se revisan en simulación física; la decoración puede superar esas pendientes sin convertirse en ruta válida.

`GEO-006 · P0` A cada lado hay 2,5–4 m de zona recuperable. Más afuera hay barrera continua de 1,2 m de alto con collider de forma simple y material de fricción; en acantilados mineros la barrera es de 1,8 m y hay plano de rescate inferior. Las defensas no tienen huecos >0,3 m ni extremos que enganchen ruedas. El tramo de salida tiene separación visual entre pits decorativos y calzada; los pits no son atajos.

### 6.2 Plano operativo por sectores

| Sector | `s` | Elementos transitables | Elementos NO transitables | Riesgo y decisión |
|---|---|---|---|---|
| Transporte | 0–335 | recta, dos carriles amplios, bahía superficial de retorno sin ventaja | tractomulas aparcadas, contenedores, muelles | elegir trazada antes del primer giro; no hay obstáculos móviles sorpresivos |
| Minas | 335–660 | ascenso, chicana, giro a meseta | tolvas, excavadoras, cinta transportadora, precipicio | frenar para chicana o abrir trazada; defensa alta impide caída casual |
| Izajes | 660–1015 | recta alta y curva larga | grúas, bobinas, contrapesos, pasarela sobre pista | sostener derrape en curva amplia; sombras no ocultan pickups |
| Retorno | 1015–1357 | descenso y curva final | patio interior, depósitos y estructura de meta | gestionar boost sin saltarse línea o checkpoint |

`GEO-007 · P0` No existe un atajo competitivo intencional en v1. Cualquier conexión entre sectores por el interior tiene barrera y decoración inequívocas; cruzar el terreno nunca permite ganar una vuelta. Los caminos de servicio se representan con textura distinta, señal de acceso cerrado y collider.

### 6.3 Puntos exactos de interés

| Elemento | Ubicación `s` | Posición lateral `d` | Reglas |
|---|---:|---:|---|
| Parrilla 1–8 | -18 a -46 m antes de meta | ±2,5 / ±6,5 m alternos | Dos columnas, 4 filas, separación longitudinal 7 m |
| Fila de poderes A | 215 m | -5 / 0 / +5 m | Tres módulos independientes; después de recta inicial |
| Zona boost 1 | 420–430 m | ancho 10 m centrado | Tras girar a minería, visible 30 m antes |
| Fila de poderes B | 540 m | -5 / 0 / +5 m | Después de chicana, nunca dentro de frenada |
| Fila de poderes C | 865 m | -5 / 0 / +5 m | Sector izajes, antes de curva amplia |
| Zona boost 2 | 1040–1050 m | ancho 10 m centrado | Sale de sector alto; boost insuficiente para volar barrera |
| Fila de poderes D | 1175 m | -5 / 0 / +5 m | Retorno, antes de curva final |
| Meta | 0 m | todo el ancho | Plano direccional y pórtico visible |

Los valores `s` son estaciones aproximadas sobre la referencia inicial. Al congelar el spline, se convierten a coordenadas exactas generadas y se guardan con versión; no se ajustan manualmente a ojo. Las tres unidades de cada fila aparecen lado a lado y separadas ≥4,5 m entre centros. Cada una tiene collider trigger, temporizador de respawn individual y confirmación visual/sonora de recogida.

`GEO-008 · P0` Checkpoints de vuelta en `s` ≈ 170, 350, 510, 680, 850, 1020 y 1190 m, más meta. Se cruzan en orden, en sentido correcto y dentro de corredor lateral permitido. Los puntos de rescate se sitúan **5 m antes** de cada checkpoint, fuera de filas de poderes, boosts y curvas de radio mínimo; una validación automática comprueba que no tocan otro collider. Rescatar nunca concede distancia gratuita hacia el siguiente checkpoint.

### 6.4 Límites y recuperación: comportamiento obligatorio

`RF-010 · P0` Dentro del ancho transitable: agarre completo. En la franja recuperable: velocidad máxima 55 % de la normal, polvo y vibración ligera; no se permite cargar derrape ni boost nuevo. Contra barrera: rebote amortiguado, sin teletransporte ni giro instantáneo.

`RF-011 · P0` Al caer, quedar boca arriba >2 s, estar inmóvil contra geometría >4 s con acelerador activo o permanecer fuera del polígono autorizado >2 s: comenzar rescate de 1,5 s con aviso visible. Reaparecer en el último punto seguro validado, velocidad 0, orientación de pista y **2 s de inmunidad a choques**; perder el poder equipado si hubo caída, no si fue atasco provocado por bug. El rescate nunca adelanta al checkpoint máximo válido.

`RF-012 · P0` El botón de rescate manual (`R`, mantener 1 s) está disponible si el vehículo lleva 3 s por debajo de 5 km/h o está fuera de pista. En carrera multijugador conlleva penalización fija de 2 s y se registra; nunca permite saltar sectores.

`QA-010` En 100 recorridos de cada borde, ningún vehículo atraviesa defensa, se hunde por la malla, queda atrapado más de 5 s o gana posición mediante rescate. Probar los 8 vehículos de parrilla y las tres carrocerías con boost e invencibilidad activos.

## 7. Vehículos y modelos 3D

`RF-020 · P0` Tres modelos base seleccionables, con **igual tamaño de hitbox competitiva** (aprox. 2,2 m ancho × 3,8 m largo × 1,7 m alto) y punto de cámara equivalente. Elementos como gancho, remolque y tolva se animan o simulan visualmente sin extender el volumen de colisión del jugador. Cada modelo tiene punto de anclaje de poder, escape de boost, ruedas y sombra clara.

| Familia / modelo | Silueta y función visual | Aceleración 0–60 km/h (`VAL`) | Velocidad máxima (`VAL`) | Giro / derrape (`VAL`) |
|---|---|---:|---:|---|
| **Izajes / Grúa Z-7** | pequeño chasis bajo, cabina lateral, pórtico plegado y gancho asegurado | 3,4 s | 87 km/h | entra rápido al derrape, menor tracción sobre grava |
| **Transporte / Tracto T-9** | tractomula compacta con quinta rueda y semirremolque corto estilizado | 3,8 s | 92 km/h | radio amplio, buena estabilidad al choque |
| **Minas / Volqueta M-4** | cabina protegida, tolva facetada y ruedas robustas | 3,6 s | 89 km/h | mejor agarre en tierra, menor respuesta inicial de dirección |

`BAL-001 · P0` Antes de publicar, la diferencia mediana de tiempo en una vuelta sin poderes entre modelos, controlados por el mismo piloto en 10 intentos cada uno, debe ser ≤2 %. Si no se cumple, ajustar parámetros; no prometer “equilibrio” por tener números parecidos. Mantener aceleración y máxima dentro de ±7 % entre familias.

`ART-010 · P0` Cada carro se modela como vehículo creíble pero caricaturizado: cabina con cristal, guardabarros, luces, parrilla, espejos flexibles, suspensión visible, ruedas con banda, tornillería grande, desgaste moderado y pintura de mantenimiento. No debe ser una caja monocroma con cuatro cilindros. El modelo de izaje muestra gancho bloqueado; la tractomula tiene remolque compacto integrado que no se articula físicamente en v1; la volqueta tiene tolva cerrada durante carrera.

`ART-011 · P1` Para cada modelo: vista frontal/lateral/trasera, silueta a 50 m, materiales PBR estilizados, LOD0/1/2, collider separado de la malla, pivote en centro de masa, ruedas nominales, luces/emisión y cuatro libreas por familia. Las libreas no cambian estadísticas. No usar logos de fabricantes reales.

`RF-021 · P0` Las ruedas giran según velocidad y dirección; la suspensión se comprime en baches pequeños; la carrocería inclina máximo 7° en curva; chispas de derrape salen de contacto con suelo. En impacto, animación de sacudida 0,25–0,4 s y reducción de velocidad, manteniendo dirección recuperable. Nada de giros de 180° por un roce lateral.

`RF-022 · P0` Una skin distinta del mismo modelo no altera collider, masa, centro de gravedad ni hitbox del poder. El resultado de conducción no depende del FPS de renderizado.

## 8. Controles y modelo de conducción

| Acción | Teclado por defecto | Regla |
|---|---|---|
| Acelerar | `W` / `↑` | analógico lógico 0–1; rampa de torque suave |
| Frenar / reversa | `S` / `↓` | frena primero; reversa hasta 25 km/h solo tras casi detenerse |
| Dirección | `A/D` / `←/→` | sensibilidad baja al superar 70 km/h, sin perder respuesta |
| Derrapar | `Espacio`, mantener | requiere suelo y ≥28 km/h; liberar ejecuta carga si procede |
| Usar poder | `F`, una pulsación | consume el slot al confirmar uso, no por auto-repetición |
| Mirar atrás | `C`, mantener | cámara temporal, sin invertir dirección |
| Rescate manual | `R`, mantener 1 s | solo si se cumple condición de RF-012 |
| Pausa / liberar cursor | `Esc` | pausa local de interfaz; el mundo multijugador continúa |

`UX-010 · P0` Las teclas se presentan en lobby y durante la primera carrera. Los inputs se pueden reasignar en v1.1; v1 debe detectar conflictos y ofrecer al menos alternativa con flechas. `F` nunca es derrape ni interacción contextual, para no gastar un poder accidentalmente. En web, `Ctrl` no se asigna a acelerar ni a derrapar para evitar `Ctrl+W`.

`RF-030 · P0` Simulación arcade con chasis rígido: fuerzas longitudinales, agarre lateral dependiente de velocidad/superficie, gravedad, colisiones sólidas, yaw y amortiguación. No usar solo traslación directa de la malla. El vehículo permanece controlable tras un choque, con velocidad angular limitada.

`RF-031 · P0` Derrape: al mantener Espacio sobre suelo a ≥28 km/h se reduce agarre lateral a 72 % (`VAL`) y aumenta gradualmente el ángulo de deslizamiento hasta un máximo de 18°. Para cargar boost, el jugador debe sostener curva y alternar correcciones; soltar recto sin tiempo suficiente no da bonus.

| Carga de derrape (`VAL`) | Condición | Recompensa al soltar |
|---|---|---|
| <0,8 s | curva válida | sin boost; recupera agarre normal |
| 0,8–1,7 s | carga nivel 1 | +12 % a velocidad objetivo durante 0,8 s |
| ≥1,7 s | carga nivel 2 | +16 % durante 1,2 s |

`BAL-010 · P0` Un boost de pista da +15 % durante 1,0 s; el poder nitro da +18 % durante 1,3 s. La velocidad efectiva nunca supera 110 % de la máxima base durante más de 1,5 s acumulados; boosts simultáneos **extienden duración hasta un tope**, no multiplican velocidad. No hay turbo suficiente para saltar de un sector a otro.

`RF-032 · P0` Frenado de 90 a 0 km/h en 26–34 m sobre asfalto; en grava aumenta 25 % y en metal húmedo decorativo 15 % (`VAL`). Colisión frontal a velocidad alta reduce velocidad y aplica 0,6 s de control atenuado; impacto lateral conserva al menos 55 % de velocidad si no golpea una barrera perpendicular.

`RF-033 · P1` Distintas superficies aportan feedback audiovisual y fricción identificable. El suelo de mina es más polvoriento, no arbitrariamente resbaladizo. Las bandas pintadas no cambian tracción de forma inesperada.

`RF-034 · P0` Los coches tienen colisión entre sí calculada por el servidor: no se atraviesan ni se apilan permanentemente. Un roce lateral leve altera trayectoria y sonido sin quitar más de 10 % de velocidad; un choque fuerte aplica impulso limitado y el mismo tiempo de recuperación a ambos, ponderado por velocidad relativa, no por modelo visual. En parrilla, separación física inicial evita superposición. Al reaparecer, el coche es intangible para otros durante 2 s y no puede empujarlos.

`QA-020` Con 30 y 60 FPS de render, mismo input pregrabado y timestep fijo, diferencia de recorrido ≤0,5 m tras 20 s en simulación local. Medir latencia de tecla a respuesta visual p95 ≤80 ms en equipo objetivo sin red y documentar valores reales.

## 9. Cámara, HUD y guía del circuito

`RF-040 · P0` Cámara chase con posición nominal 6,5 m detrás y 3,2 m arriba, seguimiento amortiguado y ligera mirada hacia interior de la curva. Su colisión impide atravesar barreras/grúas; al obstáculo entre vehículo y cámara, se aproxima hasta mínimo 2,2 m y recupera gradualmente. Permitir seleccionar cámara cercana o amplia antes de carrera.

`UX-020 · P0` HUD: posición `n/total`, vuelta `actual/objetivo`, tiempo de vuelta/total, minimapa con trayectorias y rivales, icono del poder equipado, botón `F`, indicador de carga de derrape, velocidad opcional y aviso de recuperación. Objetos importantes no quedan detrás del HUD en 16:9 ni 16:10.

`UX-021 · P0` El minimapa usa el spline real, no un dibujo aproximado. Sitúa meta, sentido de avance y puntos de rescate sin revelar datos de posición que no estén disponibles a todos. El sector cambia de color en panel lateral, y tres hitos gigantes reconocibles ayudan a orientarse sin mirar el minimapa.

`UX-022 · P1` Conteo de 3–2–1 visible y audible; antes de cero el vehículo queda bloqueado con rueda/escape animados. Salir antes no provoca descalificación accidental: el servidor rechaza avance y muestra aviso de salida anticipada; una penalización estética de 0,5 s solo si el lanzamiento se repite tres veces.

`UX-023 · P1` Anuncios de golpe, invencibilidad y boost muestran origen/efecto y tiempo restante. No tapar punto de fuga ni el siguiente giro. Debe existir opción de reducir movimiento de cámara, destellos y sacudidas.

## 10. Estructura de carrera, vueltas y clasificación

`RF-050 · P0` Flujo: lobby → preparación → carga sincronizada → parrilla → cuenta regresiva → carrera → resultados → lobby. La carrera no arranca hasta que los clientes conectados confirmen mapa cargado o venza timeout de 30 s; el anfitrión decide expulsar/no comenzar si falla una carga.

`RF-051 · P0` Vueltas válidas: cruzar meta en dirección correcta **después** de visitar los siete checkpoints en orden y registrar recorrido continuo de al menos 90 % de la longitud nominal dentro del corredor permitido. Un checkpoint solo valida si está dentro del corredor lateral correspondiente; atravesar su plano desde el patio interior no valida. El conteo es del servidor/autoridad de carrera.

`RF-052 · P0` Posición durante carrera se ordena por vueltas válidas, índice de checkpoint y progreso continuo `s` dentro del tramo actual. En empate de progreso, gana menor tiempo de cruce del último checkpoint; al terminar, gana menor timestamp de cruce válido de meta. La clasificación no retrocede por render/interpolación visual.

`RF-053 · P0` Si alguien termina, inicia ventana final de 30 s (`VAL`) para los demás. Quienes no completan figuran `DNF` con vuelta/progreso. Si todos se desconectan, la sala cierra. No hay “teletransporte a meta” de jugadores rezagados.

`RF-054 · P0` La carrera termina también por límite de sesión configurable 5–15 min, por defecto 10 min; si nadie completa, ordenar por progreso válido y mostrar “Tiempo agotado”. El máximo jamás deja una sala atrapada indefinidamente.

`RF-055 · P1` Registrar mejor vuelta local de la sesión, tiempo total, puestos, poderes utilizados, caídas y rescates. No publicar una tabla global antes de definir persistencia y control de trampas.

`QA-030` Intentos de cruzar meta al revés, cortar terreno interior, dar vuelta en U en un checkpoint, repetir la misma fila de poderes y desconectarse en meta no producen vueltas o recompensas extra. Ejecutar secuencia reproducible para 2, 4 y 8 jugadores.

## 11. Poderes y filas de tres módulos

`RF-060 · P0` Cada una de las cuatro estaciones tiene **una fila de 3 módulos**. Cada módulo es independiente. Al tocarlo, el servidor comprueba vehículo vivo, slot vacío, cooldown de módulo y trayectoria válida; asigna exactamente un poder, desactiva el módulo 8 s (`VAL`) y anuncia a todos su desaparición. Si dos coches lo tocan casi simultáneamente, solo uno lo obtiene.

`RF-061 · P0` Un solo espacio de inventario: al recoger se revela el icono tras una animación original de 0,6 s; pulsar `F` una vez pide uso. F mantenida o repetición del sistema operativo no gasta el siguiente poder. Un jugador con slot ocupado puede atravesar módulos sin consumirlos ni bloquear a otros.

| Poder original | Efecto y contrajuego | Duración/cadencia `VAL` | Frecuencia objetivo |
|---|---|---|---|
| **Remache triple** (“balas”) | tres proyectiles industriales en abanico corto; cada impacto reduce velocidad 20 % y bloquea derrape 0,45 s; defensa absorbe 1 golpe | disparos a 0 / 0,12 / 0,24 s, alcance 35 m | media |
| **Campo dieléctrico** (invencibilidad) | evita impactos y empujones de poderes, color/emisión únicos; sigue chocando con barreras y no invalida límites | 3,5 s; aviso 0,4 s antes de expirar | baja |
| **Impulso hidráulico** | nitro moderado, humo y sonido mecánico; la conducción no pierde adherencia | +18 % por 1,3 s, sujeto a BAL-010 | alta |
| **Mina de sujeción** | se coloca detrás sobre pista; rival la ve a ≥20 m; golpe ralentiza 22 % por 0,9 s | persiste 20 s o hasta detonar | media |
| **Pulso electromagnético** | cono frontal de 18 m, interrumpe boost activo y HUD de poder 0,8 s; no roba ni elimina un poder guardado | 1 pulso, telegráfico 0,25 s | media-baja |

`BAL-020 · P0` El daño es **pérdida temporal de velocidad**, no puntos de vida ni eliminación. Acumulación de ralentizaciones limitada a 30 % de velocidad máxima y 1,2 s; impactos durante inmunidad de recuperación no causan efecto. Un jugador nunca permanece inmóvil >1,0 s por encadenamiento de poderes.

`BAL-021 · P1` Reparto según puesto suavizado: quienes van detrás reciben algo más de impulso/defensa, quienes lideran reciben más herramientas de defensa que ataques fuertes. Tabla inicial por cuartiles: remache 25/23/20/18 %, campo 8/10/12/14 %, impulso 30/31/32/32 %, mina 22/21/20/20 %, pulso 15/15/16/16 % desde líder a último. Tras 30 carreras medir frecuencia real y ajustar; no se manipula el resultado en secreto por tiempo o nombre de jugador.

`RF-062 · P0` Proyectiles, minas y pulso nacen de anclajes del vehículo, tienen trayectoria/collider visible y consecuencias calculadas por la autoridad. No se crean “balas” cosméticas que atraviesan paredes mientras el servidor golpea por otro lugar. Los proyectiles chocan con defensas y props sólidos.

`RF-063 · P0` La invencibilidad usa brillo de contorno y audio breve, nunca invisibilidad ni destellos estroboscópicos. No permite atravesar paredes, saltarse checkpoints ni recoger más de un poder. En resultados se cuentan activaciones, no impactos bloqueados como ventaja de puntuación.

`QA-040` Recorrer cada fila por los tres carriles y con hitbox de los tres modelos; cada módulo se recoge una vez, respawnea solo tras su propio temporizador y se ve desde ≥30 m. Verificar 100 activaciones seguidas de `F` con repetición de teclado y pérdida de red simulada: cero usos dobles.

## 12. Lobby multijugador

`RF-070 · P0` Crear sala devuelve código corto aleatorio y enlace compartible. Unirse valida versión de cliente, capacidad 8, nombre saneado de 2–20 caracteres y conexión disponible. En LAN el anfitrión puede compartir IP+puerto; si hay despliegue público, exigir TLS/WSS y reglas de sesión.

`RF-071 · P0` Lobby muestra jugadores, vehículo y librea elegidos, estado listo, calidad de conexión, pista fija **Anillo de la Cantera**, vueltas, límite de tiempo, poderes habilitados y quién es anfitrión. Las selecciones de vehículo pueden repetirse; ningún usuario pierde su elección porque otro eligió el mismo modelo.

`RF-072 · P0` Anfitrión ajusta 1–5 vueltas, límite 5/10/15 min y poderes activados sí/no. Cambiar una opción devuelve todos a “no listo” para que acepten reglas nuevas. Solo el anfitrión inicia; necesita ≥2 jugadores listos, uno por conexión, y todos con mismo hash de mapa/versionado.

`RF-073 · P0` Seleccionar Grúa Z-7, Tracto T-9 o Volqueta M-4 muestra vista 3D rotatoria, silueta, sector de origen y estadísticas comparables; los números `VAL` se aclaran como valores iniciales sujetos a balance. El modelo del lobby es el mismo asset de carrera con otro LOD, no una representación falsa.

`RF-074 · P0` Desconexión durante carrera: conservar asiento y progreso 30 s; vehículo entra en control neutral, sin bloquear pista, a velocidad reducida y protegido contra ganar puestos por inercia. Si reconecta con token de sesión, se reanuda desde estado autorizado. Si expira, pasa a `DNF` y libera plaza tras resultados.

`RF-075 · P1` Si sale el anfitrión antes de iniciar, el rol pasa al participante conectado más antiguo y se anuncia. En carrera, el proceso que mantiene autoridad **no migra**; si cae el servidor, se aborta partida con mensaje claro, no se inventa un ganador. La arquitectura de v1 no promete migración de servidor entre PCs.

`RF-076 · P0` Con solo un mapa, la pantalla dice “Pista de esta versión: Anillo de la Cantera”. **No presenta una votación ficticia.** La votación se activa al agregar una segunda pista y se define como extensión con empate resuelto por semilla anunciada.

`RF-077 · P1` Entrar con una carrera ya comenzada permite observar clasificación y circuito sin ocupar parrilla; la persona puede elegir coche y marcarse lista para la próxima carrera. Si era un participante desconectado dentro de los 30 s, el flujo de reconexión tiene prioridad sobre espectar. Un espectador nunca emite inputs de conducción válidos.

`UX-030 · P0` El botón “Listo” muestra los requisitos no cumplidos (sin vehículo, conexión inestable, mapa sin cargar). El anfitrión no puede iniciar mientras un cliente aún carga; el estado se actualiza sin refrescar página ni abrir otra URL manualmente.

`QA-050` Verificar crear, unirse, sala llena, nombre duplicado, cambio de vehículo, cambio de reglas, salida del anfitrión, recarga de página, reconexión y comienzo simultáneo desde 2–8 clientes. Ningún cliente puede iniciar/cambiar reglas suplantando al anfitrión.

## 13. Plataforma elegida: C++ que se juega desde el navegador

**Decisión técnica:** el juego 3D y su simulación se escriben en **C++20**. El cliente se compila con Emscripten a **WebAssembly** y dibuja con **OpenGL ES 3.0 compatible con WebGL 2** sobre un `<canvas>`; el servidor autoritativo se compila como ejecutable C++ nativo. Una capa pequeña HTML/CSS/TypeScript controla sala, formularios, accesibilidad y carga, pero no decide movimiento, vueltas, colisiones ni poderes.

`RNF-001 · P0` En desarrollo y en LAN, el anfitrión ejecuta un solo servidor que entrega HTML, JS, Wasm, modelos y WebSocket por el **puerto TCP 3000**. En su equipo abre `http://localhost:3000`; los demás, `http://IP_LAN_DEL_ANFITRIÓN:3000/?room=CODIGO`. El cliente construye el WebSocket desde el origen de la página (`ws://IP_LAN_DEL_ANFITRIÓN:3000/ws`), sin `localhost` codificado. Puerto configurable por parámetro/variable; interfaz muestra URL LAN detectada o instructivo de obtención.

`RNF-002 · P0` El servidor se enlaza a `0.0.0.0` solo cuando el anfitrión selecciona modo LAN. Se documenta permitir TCP 3000 en firewall para red privada. El navegador y el equipo anfitrión deben estar en la misma red alcanzable; redes corporativas con aislamiento entre clientes pueden bloquearlo. No se requiere abrir puertos en el router ni publicar el servidor en Internet.

`RNF-003 · P0` Perfil de navegador: Chrome/Edge/Firefox recientes con WebGL 2 habilitado y WebAssembly. Antes del lobby se detecta soporte; si falta, se muestra diagnóstico concreto. No se añade WebGPU como requisito de v1. El render C++ usa VBO/VAO, shaders GLSL ES 3.00 y texturas compatibles con WebGL 2; se evitan APIs de OpenGL de escritorio y extensiones obligatorias.

**Por qué no Vulkan en v1:** Vulkan es API gráfica nativa; la pestaña expone WebGL o WebGPU. WebGPU existe, pero su cobertura y requisito de contexto seguro son condiciones adicionales para la LAN por HTTP. Cambiar a Vulkan nativo obligaría a distribuir una aplicación a cada compañero. Se deja una interfaz `RenderBackend` para evaluar WebGPU o ejecutable de escritorio más adelante, sin imponer esa complejidad a la primera carrera.

**C++ frente a alternativas:**

| Opción | Alineación con URL LAN y C++ | Decisión |
|---|---|---|
| C++20 → Wasm + OpenGL ES 3/WebGL 2 | Mantiene núcleo C++ y navegador sin instalación | **Elegida** |
| C++20 + Vulkan/OpenGL de escritorio | Excelente para binario local; cada jugador debe instalarlo | Posible puerto posterior |
| TypeScript + Three.js | Desarrollo más rápido y buen soporte web; no cumple preferencia de núcleo C++ | No elegida |
| C++ → Wasm + WebGPU | Ruta moderna; más restricciones de navegador/red y más trabajo de renderer | Investigación futura |

**Fuentes técnicas primarias:** [Emscripten: OpenGL/WebGL](https://emscripten.org/docs/porting/multimedia_and_graphics/OpenGL-support.html), [Emscripten: WebSockets](https://emscripten.org/docs/porting/networking.html), [MDN: WebGL](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API), [MDN: WebGPU](https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API), [Boost.Beast: servidor HTTP y WebSocket](https://www.boost.org/latest/libs/beast/doc/html/beast/examples.html).

### 13.1 Módulos y límites de responsabilidad

| Módulo | Lenguaje/tecnología | Autoridad y responsabilidad |
|---|---|---|
| `racing-core` | C++20 compartido | Matemática de pista, parámetros de vehículo, reglas de vuelta/poder, serialización versionada |
| `racing-client` | C++20 → Wasm | Input, predicción local, interpolación remota, cámara, audio de carrera, render y HUD 3D |
| `racing-server` | C++20 nativo + Boost.Asio/Beast | HTTP estático, WebSocket, salas, simulación autoritativa, tiempos, resultados |
| `racing-physics` | Jolt Physics C++ | Chasis rígido, ruedas virtuales, contactos y consultas; perfil reducido en cliente si pasa presupuesto |
| `racing-web` | HTML/CSS/TypeScript mínimo | Nombre, sala, selección y configuración, errores de conexión; ningún cálculo competitivo |
| `asset-pipeline` | Blender + scripts de exportación | `.glb` visuales, pista/colliders separados, LOD, atlas, hashes y validadores |

`RNF-004 · P0` Usar CMake con dependencias y versiones fijadas, compilación nativa en Windows para servidor, toolchain Emscripten para cliente y compilación reproducible de assets. La primera tarea técnica es demostrar que un vehículo Jolt, un tramo de pista, un `.glb` y una conexión WebSocket compilan y corren tanto nativo como Wasm. Si Jolt completo eleva mucho el tamaño/costo cliente, mantener Jolt en el servidor y usar predictor C++ simplificado y corregible en el cliente; **nunca** hacer del cliente la autoridad.

`RNF-005 · P0` Servidor HTTP y WebSocket en un puerto. WebSocket del cliente puede invocarse desde C++ con la API de Emscripten (`-lwebsocket.js`) o una interfaz JS muy delgada; se elige en la prueba de integración y se registra en ADR. No usar socket TCP bruto desde la pestaña.

`RNF-006 · P1` Compilar `Release` con optimizaciones y símbolos de depuración separados. Cada binario cliente incluye versión de protocolo, hash de pista y de assets; servidor rechaza clientes incompatibles con mensaje claro. Servir `.wasm` con MIME correcto y compresión HTTP. Al cambiar versión, invalidar caché por hash de archivo.

`RNF-007 · P0` El mismo código `racing-core` se ejecuta en servidor y cliente, pero la igualdad bit a bit entre Windows y Wasm **no se presupone**. El servidor corrige predicción cada snapshot; una prueba de replay compara divergencia. Jolt documenta opciones de determinismo entre plataformas y soporte Wasm; se configuran y verifican antes de confiar en ellas. [Referencia de Jolt](https://github.com/jrouwe/JoltPhysics/blob/master/Docs/Architecture.md).

### 13.2 Flujo de ejecución y protocolo

```text
Navegador amigo ── HTTP GET / ──► Servidor C++ en PC anfitrión :3000
                ◄─ HTML/CSS/JS/Wasm/GLB ────────────────┘
Cliente C++/Wasm ── WS /ws: inputs, ready, activar poder ─► Servidor C++
Cliente C++/Wasm ◄─ snapshots, eventos, vueltas, resultados ─ Servidor C++
Servidor C++ ── tick fijo de física/reglas ──► estado autoritativo por sala
```

`RED-001 · P0` Tick físico servidor 60 Hz; input de cliente 30 Hz con `sequence`, timestamp local acotado y botones; snapshots 20 Hz con estado comprimido de hasta ocho coches, filas de poderes y eventos. Cliente renderiza a frecuencia de pantalla, interpola rivales con retardo objetivo de 100 ms (`VAL`) y predice su propio coche. Timestamps y secuencias evitan aplicar inputs viejos tras reconectar.

`RED-002 · P0` Enviar **intención** (acelerar, frenar, giro, derrape, F), nunca posición ni resultado decidido por cliente. Servidor limita frecuencia, valida estado de carrera, potencia, cooldown, progreso de pista y poses posibles. Cada uso de poder tiene ID monotónico para deduplicar tras reintento.

`RED-003 · P0` Mensajes versionados: `Hello/Welcome`, `LobbyState`, `Ready`, `SelectVehicle`, `Configure`, `Start`, `Input`, `Snapshot`, `Pickup`, `UsePower`, `Lap`, `Finish`, `Reconnect`, `Error`. Definir esquema binario estable para snapshots y formato legible para configuración; validar límites de longitud y campos en ambos extremos.

`RED-004 · P1` Ping/latencia y pérdida visibles solo como indicadores de calidad, sin prometer competitividad perfecta. Objetivo LAN: RTT mediana <40 ms, p95 <100 ms; si p95 >150 ms durante 10 s se avisa y se conserva control sin saltos grandes. Al reconectar, snapshot completo y reanclaje de predicción.

`RED-005 · P0` Mantener proceso autoritativo separado del navegador anfitrión. Cerrar su pestaña no debe detener servidor ni partida; cerrar el ejecutable sí aborta con aviso. Una sala tiene semilla y reloj del servidor; reiniciar el proceso no reanuda una carrera activa en v1.

## 14. Audio, feedback e identidad del mundo

`ART-020 · P1` Cada familia tiene motor propio construido por capas de ralentí/aceleración y tono continuo sin salto audible. Deslizamiento de neumáticos cambia por asfalto/grava, impacto metálico por intensidad, suspensión golpea al aterrizar, objeto recogido suena distinto a objeto activado. Fila de poderes emite zumbido suave audible a 15–25 m, sin saturar mezcla con tres módulos.

`ART-021 · P1` Música instrumental original de energía arcade-industrial; bucle de 90–120 s con transición de última vuelta. La música baja 3–6 dB durante alertas de dirección/impacto. No utilizar melodías, efectos vocales ni arreglos reconocibles del juego de referencia.

`ART-022 · P1` Audio espacial: rival que se aproxima por detrás, proyectil frontal, maquinaria lateral. La señal de invencibilidad es legible sin audio por contorno y temporizador. Ajustes separados para música, efectos y UI; subtítulos breves para avisos esenciales.

`UX-040 · P0` Cada evento importante genera respuesta en ≤100 ms local para quien lo provoca; la corrección del servidor puede confirmar/rectificar sin duplicar sonido ni partículas. Al recoger: desaparición local predicha + confirmación; si hubo carrera entre dos jugadores, el cliente perdedor restaura el módulo sin dejar poder fantasma.

## 15. Producción de arte y datos de pista

`ART-030 · P0` Primero pista gris: malla vial, líneas de borde, colliders, rampas, barreras, minimapa y postes de giro. Un piloto debe terminar diez vueltas sin objetos de arte final ni intervención del desarrollador. Después se agregan hitos y props por sector; cualquier prop nuevo pasa prueba de visibilidad y colisión.

`ART-031 · P0` Assets externos creados en Blender con nombres y colecciones `VISUAL`, `COLLISION`, `SOCKETS`, `LOD`. Exportar glTF 2.0/GLB en metros y eje acordado; pivotes verificables, normales corregidas, UV y texturas empaquetadas. Al importar, un validador comprueba dimensiones, transformaciones, materiales, LOD y que no existan colisiones implícitas por malla artística.

| Asset / familia | Instancias v1 | LOD0 triángulos (`VAL`) | Texturas máximas | Collider |
|---|---:|---:|---|---|
| Grúa Z-7, Tracto T-9, Volqueta M-4 | 3 modelos × 4 libreas | 8–14 mil c/u | atlas 1024² color + normal/ORM | OBB compartido + ruedas virtuales |
| Superficie y bordes del circuito | 1 sistema de tramos | 80–120 mil visibles | atlas 2048² sectorizado | malla simplificada + barreras segmentadas |
| Grúas, tolvas, tractomulas estacionadas | 20–35 | 1–5 mil c/u | atlas 1024² por familia | cajas/cápsulas simples, fuera de pista |
| Vallas, balizas, señales, luces | 180–260 | 80–500 c/u | atlas compartido 1024² | collider solo en defensa real |
| Módulos de poder | 12 | 400–800 c/u | atlas 512² | sensor esférico de radio 1,2 m |
| Proyectil, mina, pulso y FX | pools acotados | ≤500 por evento principal | atlas 512² | esfera/cápsula/sensor por tipo |

`RNF-010 · P0` Presupuesto objetivo en 1280×720 y ocho vehículos: 60 FPS mediana, 1 % low ≥45 FPS en máquina de referencia **definida al empezar QA** (CPU/GPU/RAM/navegador registrados). GPU draw calls p95 ≤160; memoria de pestaña ≤800 MB; carga inicial transferida ≤35 MB comprimidos. Estos valores son objetivos y se revisan con mediciones, no se declaran cumplidos por diseño.

`RNF-011 · P0` Instancing para vallas, señales y props repetidos; LOD por distancia, frustum culling, límites de partículas por pantalla y sombras solo en objetos relevantes. La carrera mantiene aspecto reconocible en modo bajo: se recortan sombras, polvo y distancia de props, **nunca** límites, señales de curva ni poderes.

`RNF-012 · P1` Compilar shaders durante pantalla de carga cuando sea posible; precargar modelos de los tres vehículos y efectos de los cinco poderes antes de la cuenta regresiva. Tras entrar al circuito, no hay fetch bloqueante de asset crítico. Cada recurso GPU tiene propietario y liberación al salir de escena.

`ART-032 · P1` Paquete de referencia previo al modelado final: hoja ortográfica de cada vehículo, paleta/materiales, tres vistas del circuito (desde parrilla, chicana minera y curva de izajes), diagrama de lectura de bordes y referencias de audio. Esos bocetos son originales y se aprueban contra las siluetas y pruebas de visibilidad del documento.

## 16. Estructura de datos, errores y seguridad de una sala LAN

`RED-010 · P0` Cada sala tiene `roomId`, código compartible, versión de protocolo, hash de pista, host, configuración, semilla, fase, lista de participantes y reloj monotónico del servidor. Cada coche tiene `playerId`, modelo, librea, pose, velocidad lineal/angular, vuelta, checkpoint siguiente, progreso `s`, poder, cooldown, estado de inmunidad y tiempo de desconexión. Estos campos tienen tipos y límites explícitos; ningún nombre de usuario se interpola como HTML.

`RED-011 · P0` El servidor genera códigos con suficiente entropía y evita colisiones entre salas activas. Token de reconexión separado del código público; guardado en sesión del navegador, no mostrado en la URL. Un código permite entrar, no administrar la sala. Mensajes de configuración e inicio verifican identidad del anfitrión.

`RED-012 · P0` Limitar tamaño de mensaje, mensajes por segundo, número de salas y conexiones por IP para que un cliente defectuoso no congele el anfitrión. Verificar valores finitos (`NaN`/infinito rechazados), rangos de giro y tiempo, cadenas UTF-8 y secuencias de input. Registrar errores con código interno y mensaje comprensible al jugador, sin exponer rutas locales del PC.

`RED-013 · P1` En LAN por HTTP se asume red de confianza; si se abre el servicio fuera de la LAN, no basta con compartir IP pública: se requiere HTTPS/WSS, controles de acceso y revisión de seguridad. El botón de lobby indica “Sala local” para no confundirlo con servicio público.

`RF-080 · P0` Si el navegador pierde WebGL o contexto de GPU, pausar representación local y mostrar recuperación; el servidor conserva su plaza durante el plazo de reconexión. Si una descarga `.wasm` o `.glb` falla, el lobby no marca al jugador listo y ofrece reintento sin reiniciar toda la sala.

## 17. Casos de uso completos

### CU-01: crear y comenzar carrera

1. Anfitrión inicia el ejecutable C++ en su equipo; este muestra `http://localhost:3000` y la dirección LAN disponible.
2. Abre la página, verifica WebGL 2 y carga del paquete de pista/vehículos.
3. Ingresa alias; crea sala; obtiene código y enlace LAN.
4. Elige vehículo/librea, 3 vueltas, 10 min, poderes activos; marca listo.
5. Uno o más compañeros abren el enlace, ven la pista, eligen y marcan listo.
6. Anfitrión inicia; servidor verifica versiones y assets; todos aparecen en la parrilla con posiciones consistentes.
7. Cuenta 3–2–1 y habilita motor. HUD muestra clasificación, vuelta y minimapa.
8. Cada checkpoint, objeto, boost, derrape y cruce se valida. Primer puesto termina; el resto dispone de ventana final.
9. Resultados muestran puestos, vueltas y tiempos; se vuelve al lobby con mismos participantes.

**Excepción:** si un cliente no termina de cargar en 30 s, queda no listo y la carrera no empieza con él. Si cae el servidor, todos reciben “Partida interrumpida” al agotar conexión, sin falso resultado.

### CU-02: recoger y activar poder con F

1. Coche con slot libre cruza uno de tres módulos de una fila.
2. Cliente predice feedback; servidor resuelve propiedad del módulo y sortea poder según puesto/semilla.
3. HUD revela poder; servidor envía evento a todos y activa cooldown del módulo elegido.
4. Jugador pulsa F una vez. Cliente envía ID de uso, muestra respuesta inmediata reversible.
5. Servidor valida slot, estado de carrera y objetivo, consume poder una vez y emite evento con trayectoria/tiempo.
6. Los demás ven aviso y efecto; un golpe produce ralentización dentro del tope BAL-020.

**Excepción:** pulsar F con slot vacío no consume nada y muestra un aviso mínimo; mantener F no repite activación; si hay pérdida de confirmación, un reenvío con mismo ID no duplica poder.

### CU-03: caída o atasco

1. Coche sale por una zona no transitable o queda invertido; se muestra cuenta de rescate.
2. Servidor selecciona el último punto de rescate asociado al progreso válido, no al punto físicamente más cercano.
3. Tras 1,5 s reaparece parado, tangente a pista e inmune a golpes 2 s.
4. HUD/minimapa indican recuperación y la clasificación se recalcula con progreso válido.

**Excepción:** ante una penetración de collider por error, el servidor prioriza una pose libre de obstáculos y registra incidencia con `mapHash`, `s`, `d` y vehículo.

## 18. Plan de producción y dependencias

Estimación para **una persona con experiencia intermedia en C++/gráficos 3D** y apoyo puntual de arte/audio. Son **persona-semanas**, no una fecha prometida. La combinación C++ + WebAssembly + red + arte 3D aumenta esfuerzo frente a un prototipo puramente web. Rango total inicial: **30–42 persona-semanas**; puede reducirse con dos perfiles trabajando en paralelo, pero no por simple división entre dos.

| Fase | Entregable comprobable | Dependencias | Esfuerzo |
|---|---|---|---:|
| 0. Diseño y mediciones | contrato de pista congelable, siluetas y equipo objetivo | este documento | 2–3 semanas |
| 1. Plataforma C++/Wasm | canvas WebGL 2, servidor C++ HTTP+WS, coche físico y carga GLB en dos máquinas | Emscripten, CMake, Jolt/Beast | 3–5 semanas |
| 2. Circuito gris definitivo | spline, anchos, barreras, checkpoints, rescate, minimapa y pruebas de trazada | fase 1 | 4–6 semanas |
| 3. Carrera multijugador | sala, ready, 8 plazas, predicción, clasificación, reconexión y resultados | fases 1–2 | 5–7 semanas |
| 4. Conducción y poderes | derrape, boosts limitados, 4 filas triples, 5 poderes y balance inicial | fases 2–3 | 4–6 semanas |
| 5. Arte y sonido original | tres vehículos, props sectoriales, pista final, LOD, música/FX | geometría de fase 2 congelada | 6–8 semanas |
| 6. Pulido y validación | rendimiento, red LAN real, accesibilidad, documentación, bugfix | todas | 6–7 semanas |

Las fases 3 y 5 pueden solaparse tras congelar la geometría. **Bloqueos principales:** compilación Jolt/GLB en Wasm, precisión de físico al reconciliar, bugs de pista por arte añadido, redes de oficina aisladas y carga de assets excesiva. El responsable registra cada riesgo con reproducción, impacto, dueño y decisión; si falla el servidor nativo con Beast o el build WebGL 2 en el equipo objetivo, no se comienza a producir 35 props finales.

### 18.1 Orden de implementación por cortes verificables

1. Pista gris, un coche y vuelta válida sin poderes; controles y barreras ya funcionan.
2. Dos navegadores de la LAN ven el mismo coche y completan una vuelta sin divergencia persistente.
3. Lobby de hasta ocho y tres vehículos con colisiones iguales.
4. Cuatro filas de tres módulos y los cinco poderes con reglas autoritativas.
5. Arte final sobre geometría congelada, sonido y optimización.
6. Pruebas de aceptación completas y empaquetado del servidor.

Una captura bonita de pista sin vuelta verificable no cierra ninguna fase. Cada fase termina con vídeo corto, métricas y resultado de pruebas adjuntos al cambio de versión.

## 19. Verificación, métricas y criterios de juego terminado

### 19.1 Matriz de aceptación

| ID | Prueba ejecutable o demostración | Umbral de aprobación |
|---|---|---|
| `QA-001` | Abrir URL LAN en dos PC, unirse a mismo código | ambos visibles y listos sin editar URL de WebSocket |
| `QA-002` | Carrera 3 vueltas con 2, 4 y 8 jugadores | un ganador consistente, sin vueltas duplicadas ni tiempo invertido |
| `QA-003` | Recorrer 100 veces ambos bordes con tres vehículos | 0 atravesamientos y 0 atascos irreversibles |
| `QA-004` | Atravesar fila de 3 a distintas velocidades/carriles | 1 módulo por contacto, sin consumos duplicados |
| `QA-005` | Activar F 100 veces con pulsación, auto-repeat y paquete repetido | 1 uso por poder; ninguno con slot vacío |
| `QA-006` | Derrape nivel 1/2 + boost de pista + nitro | topes de BAL-010 en toda combinación |
| `QA-007` | Cortar interior/retroceder/cruzar meta a la inversa | 0 vueltas falsas |
| `QA-008` | Caída, vuelco, atasco, R manual | vuelve a lugar seguro sin adelantar checkpoint |
| `QA-009` | Desconectar/reconectar a 5, 20 y 31 s | preserva asiento ≤30 s; luego DNF claro |
| `QA-011` | Jugar 20 min con 8 coches en equipo objetivo | FPS, memoria, draw calls dentro de RNF-010 |
| `QA-012` | Pérdida 0/2/5 % y latencia 10/60/150 ms simuladas | sin teletransportes >3 m frecuentes; caída de conexión se comunica |
| `QA-013` | Cambiar reglas de lobby cuando todos están listos | ready se reinicia y nadie empieza con reglas viejas |
| `QA-014` | Navegador sin WebGL 2 / asset corrupto / servidor cerrado | error explicativo y retorno al lobby/menú |
| `QA-015` | Piloto nuevo sin ayuda, tres vueltas con pista gris | ≥80 % termina sin abandonar ni perderse; anotar puntos confusos |

`RNF-020 · P0` Registrar tiempos, FPS, 1 % low, draw calls, memoria y tamaño transferido con navegador, GPU, resolución y número de jugadores. Una medición de un solo PC no certifica rendimiento LAN. Probar al menos GPU integrada y equipo con GPU dedicada si están disponibles, y publicar los resultados junto al build.

`RNF-021 · P0` Cada cambio de física/pista ejecuta replay de input grabado, chequeo de continuidad del spline, no intersección de bordes, altura/pendiente, checkpoints en orden y puntos de rescate libres. Cada cambio de protocolo ejecuta prueba de compatibilidad/rechazo entre versiones.

`RNF-022 · P1` Pruebas humanas con al menos seis personas distintas del equipo: preguntar dónde percibieron límite de pista, qué curva fue sorpresiva, si entendieron F/derrape y si identificaron los tres tipos de vehículo. Corregir **antes** de aumentar detalle visual, porque más props pueden ocultar el problema.

**Bloqueadores de entrega:** partida que no puede terminar; inconsistencia de ganador; atajo ilegal; cliente que cae al recoger poder; choque invisible; barrera atravesable; un coche no seleccionable; F que consume dos veces; URL LAN incorrecta; rendimiento <30 FPS sostenidos en el equipo mínimo acordado; asset ajeno sin licencia comprobable. Ninguna mejora cosmética compensa estos fallos.

### 19.2 Evidencias del paquete de revisión

- Código fuente C++, configuración de build nativo/Wasm, dependencias fijadas e instrucciones de reconstrucción.
- Build distribuible con servidor Windows, cliente `.wasm`, HTML/CSS/JS, pista y tres modelos.
- Diagrama de pista con puntos, anchos, límites, checkpoints y filas de poderes; hash de mapa exportado.
- Capturas/vídeo de lobby 2 PC, vuelta completa, derrape, activación de F, choque/rescate y pantalla de resultados.
- Reporte de QA-001 a QA-015, métricas RNF-010, incidencias abiertas y decisiones de balance.
- Créditos/licencias de todos los modelos, texturas, fuentes y sonidos, incluso si se crean internamente.

## 20. Relación con el PDF del taller de Unity

El archivo `Taller12026.pdf` del repositorio pide explícitamente un **proyecto Unity** con escena y GameObjects, Rigidbody, colliders/triggers, variables editables en Inspector, diez materiales, un Physic Material, cinco modelos externos y entrega de proyecto Unity comprimido. **Este plan C++/WebGL 2 se elige para acceso por navegador y LAN; por sí mismo no cumpliría una entrega que exija Unity.** Si Mantenimiento Racing se presentará a ese taller, habrá que acordar una versión Unity separada o cambiar el motor antes de afirmar cumplimiento. Las mecánicas de pista, colisiones, triggers de módulos y condiciones de finalización sí pueden trasladarse conceptualmente.

## 21. Decisiones pendientes antes de escribir código de producción

1. Registrar CPU, GPU, RAM, navegador y resolución del PC anfitrión y de uno o dos compañeros; fijar equipo mínimo y perfil RNF-010.
2. Confirmar si la red del trabajo permite conexiones entre equipos y abrir TCP 3000 en perfil privado; probar con un servidor HTTP simple y otro PC.
3. Revisar en vista cenital el trazado GEO-002, una vuelta gris y los anchos en chicana. Aceptar o versionar coordenadas antes de arte final.
4. Aprobar hojas de silueta de Grúa Z-7, Tracto T-9 y Volqueta M-4, nombres y paleta.
5. Congelar versión concreta de Emscripten, Jolt, Boost, compilador y formato de assets al superar fase 1; registrar en archivo de dependencias/ADR, no en una frase que envejece.

**Regla de control de cambios:** una solicitud nueva debe indicar requisito afectado, impacto en mapa/servidor/arte/pruebas, costo estimado y criterio de aceptación. Las coordenadas, pesos de poderes y topes de velocidad no cambian silenciosamente entre builds; se versionan con el mapa y aparecen en notas de versión.
