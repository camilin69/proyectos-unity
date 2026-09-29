# MANTENIMIENTO STRIKE

## Plan maestro de requisitos para un shooter táctico web 3D con Three.js

Versión: 1.0  
Estado: planeación; no implementado  
Plataforma inicial: navegador de escritorio  
Modalidad principal: partidas tácticas por rondas, 5 contra 5  

---

## 1. Cómo leer este documento

Este archivo define el producto, la arquitectura técnica, las mecánicas, el contenido y los criterios de aceptación. Debe utilizarse como fuente de planeación antes de comenzar el desarrollo.

Orden recomendado:

1. Leer las secciones 2–6 para entender el juego y su alcance.
2. Adoptar la arquitectura de las secciones 7–12 antes de escribir sistemas jugables.
3. Construir el proyecto en las etapas de la sección 22.
4. Validar cada etapa con las pruebas de las secciones 23–25.
5. Registrar cualquier cambio de balance o arquitectura en el documento.

Clasificación de requisitos:

- **OBL:** necesario para considerar completa la primera versión jugable.
- **IMP:** necesario para la versión pública, pero puede llegar después del primer prototipo.
- **OPT:** mejora posterior que no debe retrasar el núcleo del juego.
- **VAL:** valor inicial que debe ajustarse mediante pruebas.

Este juego puede inspirarse en la tensión, economía y claridad de los shooters tácticos competitivos, pero debe utilizar nombres, mapas, armas, sonidos, modelos, interfaz y dirección artística originales.

---

## 2. Recomendación de framework

### 2.1 Elección principal

Utilizar:

- **React 19 + TypeScript** para la aplicación y la interfaz.
- **Vite** para desarrollo y compilación.
- **Three.js** como motor de renderizado 3D.
- **React Three Fiber** como integración declarativa entre React y Three.js.
- **@react-three/drei** para utilidades de cámara, loaders y helpers.
- **Rapier** mediante `@react-three/rapier` para colisiones y físicas.
- **Zustand** para estado de sesión, HUD, inventario y flujo de partida.
- **Colyseus** para servidor de partidas y sincronización multijugador autoritativa.
- **Node.js + TypeScript** para backend de juego.
- **WebSocket seguro** para comunicación en tiempo real.

### 2.2 Por qué React es la mejor opción para este proyecto

React Three Fiber conserva el acceso a Three.js y aporta un ecosistema maduro para composición de escenas, carga de modelos, postprocesado, físicas y herramientas de desarrollo. React también facilita HUD, menús, inventario, marcador, compra de armas, autenticación y navegación sin mantener dos sistemas de interfaz separados.

La simulación del shooter no debe depender de renders de React. El movimiento, los disparos, la predicción y los ticks del servidor se implementan como sistemas deterministas o stores externos. React representa la escena y la interfaz; no controla la verdad competitiva de la partida.

### 2.3 Comparación

| Alternativa | Ventajas | Limitaciones para este proyecto | Decisión |
|---|---|---|---|
| React + R3F | Ecosistema grande, UI madura, Drei/Rapier, abundantes ejemplos y perfiles disponibles | Es fácil abusar de renders y estados React dentro del loop | **Elegida** |
| Svelte + Threlte | Sintaxis compacta y excelente reactividad | Ecosistema 3D y multijugador más pequeño | Buena alternativa, no baseline |
| Vue + TresJS | Vue es claro y familiar para aplicaciones | Menor ecosistema específico de juegos Three.js | No elegida |
| Three.js puro | Control directo y menor abstracción | Más código para UI, ciclo de vida y herramientas | Útil dentro de sistemas críticos |
| Babylon.js | Más funciones propias de motor de juego | Cambiaría el requisito central de trabajar con Three.js | Fuera del baseline |

### 2.4 Regla arquitectónica

React administra componentes visuales, pantallas y montaje. El servidor administra la verdad de jugadores, disparos, daño, rondas, compras y resultados. El cliente puede predecir movimiento y efectos para reducir latencia, pero debe aceptar correcciones del servidor.

---

## 3. Concepto del juego

**Mantenimiento Strike** es un shooter táctico competitivo situado en un complejo industrial de mantenimiento automatizado. Dos equipos disputan el control de un núcleo de diagnóstico:

- **Intrusos:** deben instalar un dispositivo de interferencia en uno de dos nodos.
- **Custodios:** deben impedir la instalación o desactivar el dispositivo antes de que complete su operación.

Las partidas se dividen en rondas cortas. Cada vida importa: no hay reaparición durante la ronda. La victoria depende de información, precisión, coordinación, rutas, economía y uso responsable de utilidades.

La identidad debe alejarse de una copia visual de Counter-Strike. El complejo utiliza elevadores de servicio, pasarelas, talleres, tuberías, paneles energéticos y puertas industriales. Las armas y facciones son ficticias.

---

## 4. Pilares de diseño

1. **Legibilidad competitiva:** jugadores, coberturas, proyectiles, utilidades y objetivos se distinguen con rapidez.
2. **Tensión por ronda:** una muerte elimina al jugador hasta la siguiente ronda.
3. **Precisión con compromiso:** movimiento, retroceso y dispersión obligan a elegir cuándo detenerse y disparar.
4. **Información imperfecta:** pasos, recargas, puertas y utilidades comunican posiciones sin revelar todo el mapa.
5. **Mapas equilibrados:** rutas con tiempos medidos, coberturas justas y múltiples decisiones.
6. **Servidor autoritativo:** el cliente nunca decide por sí solo daño, dinero o victoria.
7. **Rendimiento web:** carga progresiva, memoria limitada y configuración gráfica adaptable.

---

## 5. Alcance de la primera versión

### 5.1 Vertical slice obligatorio

- Un mapa competitivo completo.
- Dos zonas de objetivo: Nodo A y Nodo B.
- Equipos de hasta 5 jugadores.
- Movimiento en primera persona.
- Una pistola, un rifle, una escopeta y un arma cuerpo a cuerpo.
- Una granada de humo y una granada de pulso cegador.
- Compra al inicio de ronda.
- Instalación y desactivación del dispositivo.
- Espectador después de morir.
- Marcador, chat de equipo y registro de eliminaciones.
- Servidor de partida autoritativo.
- Entrenamiento local con bots simples o blancos móviles.

### 5.2 Versión pública inicial

- Dos o tres mapas.
- Ocho a doce armas originales.
- Tres utilidades tácticas.
- Matchmaking casual y partidas privadas.
- Reconexión a partida.
- Configuración de controles, video, audio y accesibilidad.
- Sistema básico de perfiles y estadísticas.
- Herramientas de moderación y reporte.

### 5.3 Fuera del alcance inicial

- Mundo abierto.
- Campaña narrativa.
- Vehículos.
- Destrucción completa de escenarios.
- Mercado de objetos con dinero real.
- Intercambio de skins.
- Soporte móvil competitivo.
- Battle royale.
- Anti-cheat a nivel kernel.

---

## 6. Reglas de partida

### 6.1 Formato

| Parámetro | Valor inicial |
|---|---:|
| Jugadores | 5 contra 5 |
| Rondas para ganar | 13 |
| Máximo de rondas reglamentarias | 24 |
| Duración de compra | 20 s |
| Duración de ronda | 1 min 45 s |
| Tiempo de instalación | 3.2 s |
| Cuenta regresiva del dispositivo | 40 s |
| Tiempo de desactivación | 7 s; 3.5 s con herramienta |
| Reaparición | Solo al comenzar nueva ronda |
| Daño aliado | Desactivado inicialmente; configurable en privadas |

Todos los valores son VAL y requieren telemetría de pruebas. El cambio de lados ocurre después de 12 rondas. Empate competitivo y tiempo extra se dejan para una etapa posterior.

### 6.2 Condiciones de victoria

Intrusos ganan si eliminan al equipo contrario antes de terminar la ronda, o si el dispositivo completa su operación. Custodios ganan si eliminan a todos los intrusos antes de la instalación, si expira el tiempo sin instalación o si desactivan el dispositivo.

Después de instalar, eliminar a todos los intrusos no concede victoria inmediata: los custodios aún deben desactivar. El servidor evalúa cada resultado una sola vez.

### 6.3 Economía

- Crédito inicial: 800.
- Recompensa por victoria: 3250.
- Recompensa por derrota: escala de 1400 a 3400.
- Instalación: bonificación de equipo de 800.
- Eliminar enemigos concede recompensa dependiente del arma.
- El dinero tiene un máximo inicial de 16000.
- Compra disponible solamente durante la fase y dentro de zona autorizada.

El servidor valida saldo, fase, inventario y precio. El cliente muestra una predicción de compra, pero no crea armas ni modifica dinero.

---

## 7. Arquitectura general

```text
Navegador
├── React: menús, lobby, HUD, ajustes y resultados
├── React Three Fiber: escena Three.js y representación
├── Sistemas cliente: input, cámara, predicción, audio y VFX
├── Zustand: estado derivado de UI/sesión
└── Cliente Colyseus: snapshots, inputs y eventos

Servidor Node.js
├── Lobby y salas Colyseus
├── Tick autoritativo de partida
├── Validación de movimiento, disparos, compras y objetivos
├── Historial corto para compensación de latencia
├── Persistencia de perfiles fuera del tick
└── Logs, métricas y moderación
```

### 7.1 Monorepo recomendado

```text
apps/
  client/
  game-server/
packages/
  protocol/
  game-data/
  simulation/
  eslint-config/
assets/
  source/
  runtime/
docs/
```

Utilizar `pnpm` workspaces. Los tipos de mensajes, IDs y datos de armas se comparten mediante paquetes sin compartir secretos ni lógica autoritativa con el cliente.

### 7.2 Reglas de separación

- Los componentes React no contienen reglas autoritativas.
- El servidor no importa Three.js ni depende del DOM.
- Las definiciones compartidas son datos, tipos y matemáticas puras.
- El renderer interpola snapshots; no modifica el estado del servidor.
- Audio y partículas reaccionan a eventos confirmados o predichos reconciliables.

---

## 8. Cliente y renderizado Three.js

### 8.1 Escena

- `Canvas` único persistente.
- Cámara en primera persona con Pointer Lock.
- Escena dividida en mapa estático, personajes, viewmodel, efectos y depuración.
- Render loop `always` durante partida y `demand` en menús 3D estáticos cuando sea viable.
- Actualizaciones por frame mediante `useFrame`, evitando `setState` React cada frame.
- Objetos repetidos mediante instancing cuando no requieren rig individual.

### 8.2 Activos

- Formato runtime: glTF/GLB.
- Compresión geométrica Draco o Meshopt después de medir coste de decodificación.
- Texturas KTX2/Basis cuando el pipeline esté validado.
- Modelos con escala métrica, pivotes documentados y LOD.
- Lightmaps o iluminación horneada para arquitectura; luces dinámicas limitadas.
- Precarga solamente de activos del mapa y equipamiento necesario.

### 8.3 Rendimiento objetivo

| Perfil | Objetivo |
|---|---|
| Recomendado | 1920×1080 a 60 FPS estables |
| Compatible | 1280×720 a 45–60 FPS |
| Frame time de 60 FPS | Mediana ≤16.7 ms; p95 ≤22 ms |
| Memoria | Medir por mapa; evitar crecimiento tras varias partidas |
| Carga inicial | Objetivo ≤10 s en conexión razonable, con progreso real |

Calidad adaptable: resolución interna, sombras, SSAO, anisotropía, partículas y distancia de LOD. No reducir telegraphs, siluetas enemigas ni humo competitivo de manera que un perfil obtenga ventaja.

---

## 9. Movimiento y cámara

### 9.1 Controles base

| Entrada | Acción |
|---|---|
| WASD | Movimiento |
| Ratón | Mirar |
| Shift | Caminar silenciosamente |
| Ctrl | Agacharse |
| Espacio | Saltar |
| Clic izquierdo | Disparar |
| Clic derecho | Acción secundaria o apuntar según arma |
| R | Recargar |
| E | Interactuar/instalar/desactivar |
| 1–4 | Armas y utilidad |
| G | Soltar arma/dispositivo |
| B | Menú de compra |
| Tab | Marcador |
| Esc | Pausa/ajustes |

### 9.2 Parámetros iniciales

- Velocidad al correr: 5 m/s.
- Caminar silenciosamente: 2.4 m/s.
- Agachado: 1.8 m/s.
- Altura de cápsula: 1.8 m de pie; 1.2 m agachado.
- Salto limitado, sin bunny hopping como ventaja dominante.
- Aceleración y frenado coherentes con precisión de armas.
- Escaleras y pendientes no deben generar lanzamientos ni atascos.

El cliente envía secuencia de inputs y tiempo; el servidor simula o valida el movimiento. Las correcciones se suavizan visualmente, pero no atraviesan paredes.

---

## 10. Armas y combate

### 10.1 Modelo de disparo

- Hitscan autoritativo para armas iniciales.
- Cadencia, cargador, reserva, daño, penetración y retroceso definidos en datos versionados.
- Dispersión mayor al moverse, saltar o disparar de forma sostenida.
- Retroceso reproducible por arma con variación acotada.
- Raycast del servidor con compensación de latencia limitada.
- El cliente predice fogonazo, sonido y retroceso; confirma impacto y daño desde servidor.
- Un `ShotId` impide disparos o impactos duplicados.

### 10.2 Arsenal inicial

| ID | Función | Daño inicial | Cargador | Precio |
|---|---|---:|---:|---:|
| WPN-P01 | Pistola inicial precisa | 32 | 12 | 400 |
| WPN-R01 | Rifle automático principal | 34 | 30 | 2900 |
| WPN-S01 | Escopeta de corto alcance | 8×15 máximo | 6 | 1800 |
| WPN-M01 | Herramienta cuerpo a cuerpo | 55 frontal | N/A | Incluida |

El daño final depende de distancia, zona corporal y armadura. Headshot debe ser claro, pero su multiplicador se configura por arma. Evitar números copiados de juegos existentes sin evaluación propia.

### 10.3 Recarga y cambio de arma

La munición se transfiere en un punto de compromiso explícito. Cancelar antes conserva el estado anterior; cancelar después conserva la transferencia. Animación, audio, HUD y servidor deben coincidir. Cambiar de arma no permite superar cadencia ni duplicar munición.

### 10.4 Lag compensation

El servidor conserva un historial corto de hitboxes, limitado inicialmente a 200 ms. Al recibir un disparo, valida tiempo, cadencia y posición, rebobina solamente hitboxes relevantes y ejecuta raycast. Nunca acepta un timestamp arbitrariamente antiguo del cliente.

---

## 11. Multijugador y networking

### 11.1 Tick y snapshots

- Tick autoritativo inicial: 30 Hz.
- Inputs cliente: hasta 60 Hz, agrupados cuando convenga.
- Snapshots: 20 Hz iniciales con delta/compresión posterior.
- Interpolación remota: buffer objetivo de 100 ms.
- Predicción local y reconciliación por número de secuencia.
- Eventos fiables para ronda, compra, muerte, dispositivo y chat.

Todos son VAL. Medir ancho de banda, latencia y CPU antes de aumentar frecuencias.

### 11.2 Mensajes mínimos

`JoinRequest`, `InputFrame`, `PlayerSnapshot`, `ShotRequest`, `ShotResult`, `PurchaseRequest`, `InventorySnapshot`, `ObjectiveAction`, `RoundState`, `DamageEvent`, `DeathEvent`, `ChatMessage`, `PingReport` y `ReconnectRequest`.

Cada mensaje tiene versión, límites de tamaño y validación. No aceptar nombres, texto o arrays sin longitud máxima.

### 11.3 Desconexión

- Ventana inicial de reconexión: 60 s.
- El avatar desconectado permanece vulnerable o lo controla un bot simple según regla de cola.
- No conceder dinero duplicado al reconectar.
- El servidor conserva identidad de sesión, no el socket anterior.
- Abandono reiterado puede aplicar penalización futura.

---

## 12. Servidor autoritativo y seguridad

El servidor valida:

- Velocidad, aceleración, posición y colisión.
- Cadencia, munición, recarga y arma equipada.
- Raycasts y daño.
- Compra, saldo y zona de compra.
- Poses de instalación/desactivación y línea de interacción.
- Fase, tiempo y resultado de ronda.
- Equipo, chat y permisos de sala.

Medidas iniciales:

- Rate limits por tipo de mensaje.
- Secuencias monotónicas y protección contra replay.
- Validación de esquema en borde de red.
- Sanitización de nombres y chat.
- TLS en producción.
- Secretos solo en servidor y variables de entorno.
- Logs de eventos de seguridad sin tokens ni contraseñas.
- Política de origen y encabezados web restrictivos.

El cliente se considera manipulable. Ofuscación y minificación no son anti-cheat. Un sistema competitivo público necesitará detección estadística, revisión y moderación progresivas.

---

## 13. Mapas y diseño competitivo

### 13.1 Mapa inicial: Complejo Delta

Zonas:

- Base de Intrusos.
- Base de Custodios.
- Nodo A: sala de turbinas.
- Nodo B: depósito de piezas.
- Ruta central: pasarela de diagnóstico.
- Ruta lateral A: conductos de servicio.
- Ruta lateral B: taller y almacén.
- Conectores de rotación con riesgo y sonido característico.

### 13.2 Requisitos métricos

- Ancho principal: 2.5–4 m.
- Puertas: mínimo 1.4 m salvo choke deliberado.
- Coberturas: alturas consistentes para cabeza y torso.
- Evitar píxeles de visión involuntarios y huecos bajo geometría.
- Máximo de dos o tres ángulos críticos visibles desde una posición habitual.
- Tiempos de llegada a objetivos medidos para ambos equipos.
- Ningún spawn visible directamente desde el contrario.
- Utilidades deben poder rebotar sin atravesar paredes.

### 13.3 Proceso del mapa

1. Diagrama de rutas.
2. Blockout sin arte.
3. Medición de tiempos y líneas de visión.
4. Partidas con armas básicas.
5. Ajuste de spawns, coberturas y rotaciones.
6. Kit visual y señalización.
7. Optimización, colisión y audio.
8. Validación competitiva final.

No producir arte definitivo antes de que el blockout funcione.

---

## 14. Objetivo táctico

El dispositivo solamente puede instalarse en volúmenes autorizados. La instalación se cancela al soltar interacción, salir del volumen, morir o quedar sin línea válida. El dispositivo permanece en el mundo si su portador muere o lo suelta.

Estados:

```text
Carried → Dropped → Planting → Armed → Defusing → Defused/Detonated
```

Cada transición tiene `ObjectiveActionId` y la decide el servidor. El cliente muestra progreso derivado del tiempo confirmado. Dos jugadores no pueden instalar ni desactivar simultáneamente el mismo dispositivo.

El audio comunica inicio de instalación, final, pulsos restantes y desactivación. Los sonidos no deben revelar información que el equipo no tendría legítimamente.

---

## 15. Utilidades tácticas

### 15.1 Humo

- Proyectil físico validado por servidor.
- Rebote simplificado y trayectoria predecible.
- Volumen activo durante 15 s inicialmente.
- Visibilidad bloqueada de manera coherente para todos los clientes.
- No depender únicamente de partículas locales fáciles de desactivar.

### 15.2 Pulso cegador

- Intensidad según orientación, distancia y obstrucción.
- Duración máxima inicial de 2.2 s mirando directamente.
- Audio amortiguado breve, sin dañar audición real del usuario.
- El servidor determina efecto y duración; cliente representa transición accesible.

### 15.3 Reglas

Inventario inicial máximo: dos utilidades. No spamear partículas ni luces dinámicas. La configuración gráfica no puede volver transparente el humo ni eliminar el destello competitivo.

---

## 16. Personajes, animación y cámara

- Dos siluetas de equipo claramente distintas sin depender solo del color.
- Viewmodel separado del modelo de tercera persona.
- Clips: idle, caminar, correr, agachar, saltar, aterrizar, disparar, recargar, equipar, recibir daño y morir.
- Sincronización de pies, manos, cargadores y eventos.
- Upper-body aim offsets limitados; giros grandes mueven pies.
- Hitboxes servidoras simples vinculadas a pose autorizada.
- Cadáveres no bloquean rutas competitivas.
- Cámara de espectador nunca atraviesa zonas que revelen información ilegítima.

Animaciones no controlan por sí solas daño o munición. Los puntos de compromiso se validan por estado del servidor.

---

## 17. Dirección visual y audio

### 17.1 Arte

Estética industrial limpia pero deteriorada: metal pintado, concreto, caucho, señalización de seguridad y maquinaria. Cada zona tiene una identidad geométrica y cromática moderada. Mantener contraste entre combatientes y fondo.

Evitar:

- Oscuridad que oculte jugadores.
- Exceso de reflejos y bloom.
- Niebla competitiva fuera de utilidades.
- Skins que alteren hitbox aparente.
- Decals que parezcan enemigos o fuego activo.

### 17.2 Audio

- Pasos por metal, concreto, rejilla, caucho y agua superficial.
- Disparos con capas cercana, mecánica y cola ambiental.
- Recarga y cambio de arma audibles a distancia calibrada.
- Posicionamiento estéreo/HRTF compatible con Web Audio.
- Mezclador con maestro, efectos, voz, interfaz y ambiente.
- Variantes suficientes para evitar repetición evidente.

Audio transmite información competitiva y debe validarse con auriculares y altavoces. El volumen elegido por el usuario no altera radios lógicos del servidor.

---

## 18. Interfaz y experiencia

Pantallas:

- Inicio y autenticación opcional.
- Lista de partidas y lobby privado.
- Selección de equipo.
- HUD de partida.
- Menú de compra.
- Marcador.
- Espectador.
- Resultado final.
- Ajustes y controles.

HUD mínimo:

- Salud y armadura.
- Arma, cargador y reserva.
- Utilidades.
- Tiempo y marcador de ronda.
- Estado del dispositivo.
- Miembros vivos del equipo.
- Feed de eliminaciones.
- Indicador de red/pérdida de paquetes.

Accesibilidad:

- Reasignación de teclas.
- Sensibilidad y FOV.
- Reducción de movimiento de cámara.
- Escala de HUD y texto.
- Perfiles de color con iconos adicionales.
- Volúmenes separados.
- Subtítulos para anuncios, no para pasos enemigos.
- Reducción de destellos sin eliminar su duración competitiva.

---

## 19. Bots y entrenamiento

El entrenamiento local permite probar movimiento, puntería, retroceso, compra y objetivo sin conexión competitiva. Los bots iniciales no deben simular una IA avanzada inexistente.

Estados: patrullar, escuchar, investigar, ver enemigo, buscar cobertura simple, disparar, operar objetivo y morir. El servidor o una simulación local equivalente conserva las reglas. Los bots no atraviesan humo con información perfecta ni apuntan a través de paredes.

Un mapa de práctica incluye blancos estáticos y móviles, medidor de precisión y reinicio rápido. Las estadísticas se etiquetan como entrenamiento.

---

## 20. Persistencia y servicios web

Datos persistentes posteriores al vertical slice:

- Cuenta o identidad invitada.
- Nombre visible moderable.
- Ajustes del cliente.
- Estadísticas agregadas.
- Historial breve de partidas.
- Sanciones y reportes.

No guardar contraseñas directamente. Usar proveedor de identidad o hashes robustos con flujo implementado por librería mantenida. Separar base de datos del loop de partida; las escrituras lentas no congelan el servidor.

El resultado se registra de forma idempotente con `MatchId`. Reintentar una escritura no concede dos veces estadísticas o recompensas.

---

## 21. Datos y configuración

Definiciones centralizadas y versionadas:

- `WeaponDefinition`
- `MovementDefinition`
- `UtilityDefinition`
- `EconomyDefinition`
- `RoundDefinition`
- `MapDefinition`
- `SurfaceDefinition`
- `ProtocolVersion`

El servidor carga y valida definiciones. El cliente recibe los datos necesarios y no puede imponer otra versión. Una partida congela su revisión de balance al comenzar.

Validadores rechazan IDs duplicados, precios negativos, cargadores inválidos, tiempos imposibles, spawn fuera del mapa, objetivo sin volumen y activos inexistentes.

---

## 22. Plan de producción

| Etapa | Entrega | Criterio de salida |
|---|---|---|
| P0 | Repositorio, CI, cliente y servidor vacíos conectados | Build y tests básicos pasan |
| P1 | Movimiento local, cámara y mapa de prueba | Control estable y colisión sin atravesar paredes |
| P2 | Servidor autoritativo y dos clientes | Predicción/reconciliación medible |
| P3 | Disparo, daño, muerte y espectador | Servidor rechaza cadencia/munición inválidas |
| P4 | Rondas, equipos, objetivo y economía | Partida completa reiniciable |
| P5 | Mapa blockout 5v5 | Tiempos, rutas y spawns aprobados |
| P6 | Armas, utilidades y compra completa | Balance inicial y casos extremos verificados |
| P7 | Arte, animación, audio y UI | Legibilidad competitiva y rendimiento objetivo |
| P8 | Reconexión, persistencia y moderación | Fallos de red no duplican estado |
| P9 | QA, seguridad, accesibilidad y despliegue | Criterios de terminado cumplidos |

No comenzar P7 a escala completa antes de aprobar P5. Arte de prueba y viewmodels pueden avanzar para validar pipeline.

---

## 23. Pruebas obligatorias

### 23.1 Gameplay

- Una bala válida produce un solo daño.
- Disparar sin munición no genera hit.
- Cancelar recarga no duplica balas.
- Morir cancela instalación y disparos pendientes inválidos.
- Últimos jugadores se eliminan simultáneamente: el servidor resuelve una condición coherente.
- Dispositivo completa operación mientras el último intruso muere: prioridad definida y probada.
- Compra doble o simultánea no produce saldo negativo.

### 23.2 Red

- Latencia simulada de 20, 80, 150 y 250 ms.
- Pérdida de paquetes de 1 %, 5 % y 10 %.
- Jitter y mensajes fuera de orden.
- Reconexión antes y después de cambio de ronda.
- Dos mensajes con mismo ID.
- Cliente que envía velocidad, munición o timestamp imposibles.
- Servidor lleno, sala cerrada y versión incompatible.

### 23.3 Mapa

- Recorrer todas las rutas de pie y agachado.
- Lanzar utilidades contra cada esquina importante.
- Revisar líneas de visión desde spawns.
- Medir llegada a A/B por todas las rutas.
- Buscar posiciones fuera del mapa y píxeles de visión.
- Revisar colisión entre cadáveres, armas soltadas y puertas.

### 23.4 Web

- Chrome, Edge y Firefox actuales.
- Diferentes escalas de pantalla y DPI.
- Pérdida de foco, cambio de pestaña y Pointer Lock cancelado.
- Contexto WebGL perdido y recuperación segura.
- Audio bloqueado hasta gesto del usuario.
- Memoria tras diez partidas consecutivas.

---

## 24. Observabilidad y despliegue

Métricas servidoras:

- Tick time y ticks perdidos.
- Uso de CPU/memoria por sala.
- Jugadores y mensajes por segundo.
- RTT y pérdida por jugador.
- Rechazos de inputs y disparos.
- Duración y resultado de rondas.
- Errores de persistencia.

Métricas cliente con consentimiento y privacidad apropiada:

- FPS/frame time.
- Tiempo de carga.
- Errores WebGL.
- Desconexiones y reconexiones.
- Perfil gráfico efectivo.

Despliegues separados para frontend estático, servidores de juego y servicios persistentes. Utilizar staging antes de producción. No registrar chat completo, tokens o información sensible en logs generales.

---

## 25. Definición de terminado

La primera versión está terminada cuando:

- Una partida 5v5 puede comenzar, cambiar de lado y finalizar sin intervención manual.
- Movimiento, disparos, daño, compras y objetivos son autoritativos.
- No existen duplicaciones reproducibles de dinero, munición o resultados.
- Reconexión y abandono tienen resultados definidos.
- El mapa no contiene salidas, líneas injustas o bloqueos conocidos de severidad alta.
- El rendimiento cumple el perfil acordado en hardware de prueba.
- HUD, compra, marcador, espectador y ajustes son navegables.
- Los activos y sonidos tienen procedencia documentada.
- Las pruebas de seguridad básicas y validación de mensajes pasan.
- La build desplegada corresponde a un commit y una versión de protocolo conocidos.
- No hay errores recurrentes de consola o servidor.

Clasificación de defectos:

- **S0:** pérdida de datos, ejecución no autorizada, servidor caído o vulnerabilidad crítica. Cero abiertos.
- **S1:** exploit competitivo, softlock, resultado incorrecto o desconexión general. Cero abiertos.
- **S2:** desincronización visible, ventaja por configuración, UI esencial rota o rendimiento fuera de objetivo. Cero en flujo principal.
- **S3:** defecto cosmético sin efecto competitivo. Puede registrarse con decisión explícita.

---

## 26. Riesgos principales

| Riesgo | Respuesta |
|---|---|
| Cheating en cliente web | Servidor autoritativo, validación y detección progresiva |
| Latencia arruina disparos | Predicción, interpolación y lag compensation limitada |
| React genera renders excesivos | Estado de frame fuera de React y perfiles continuos |
| Mapas visualmente ricos pero injustos | Blockout y pruebas antes de arte final |
| Humo diferente por GPU | Representación competitiva común y pruebas por perfil |
| Descargas iniciales grandes | GLB/KTX2, división por mapa, caché versionada y precarga medida |
| Física divergente | Servidor valida trayectorias críticas; Rapier con versiones fijadas |
| Scope demasiado amplio | Vertical slice, gates P0–P9 y extensiones fuera del baseline |
| Dependencia de librerías | Versiones fijadas, adaptadores y pruebas de actualización |

---

## 27. Decisiones pendientes antes de producción avanzada

1. Nombre definitivo y lenguaje visual de las dos facciones.
2. Hosting y regiones iniciales de servidores.
3. Autenticación invitada o mediante proveedor.
4. Nivel competitivo del matchmaking inicial.
5. Presupuesto de arte, audio y operación mensual.
6. Política de moderación, privacidad y retención de logs.
7. Hardware mínimo y navegadores oficialmente soportados.

Estas decisiones no impiden crear el vertical slice local y el primer servidor de prueba. Deben resolverse antes de una beta pública.

---

## 28. Instrucción de arranque para el agente de desarrollo

> Continúa Mantenimiento Strike como un shooter táctico web 3D original desde el primer incremento descrito en la sección 30. El cliente existente usa React, TypeScript, Vite, Three.js y React Three Fiber; el servidor Node.js/TypeScript usa WebSocket directo y decide movimiento, colisiones, daño y reaparición. No dupliques ese trabajo. Avanza por los gates de la sección 22, probando dos clientes reales y convirtiendo los modelos procedurales en arte de producción por etapas. Evalúa Rapier, Zustand y Colyseus cuando sus necesidades concretas aparezcan; si migras, conserva las pruebas de comportamiento y la autoridad del servidor. Añade economía, objetivo y resultado de ronda al servidor, no al cliente. Registra versiones, pruebas, métricas y cambios de balance. Usa diseños, nombres, modelos y sonidos originales; la referencia a shooters tácticos describe el género, no autoriza copiar contenido protegido.

---

## 29. Referencias técnicas oficiales

- [React Three Fiber — documentación](https://r3f.docs.pmnd.rs/): renderer de React para Three.js. La rama 9 se empareja con React 19; fijar versiones compatibles en P0.
- [Three.js — instalación](https://threejs.org/manual/#en/installation): recomienda npm y un build tool como Vite para proyectos modernos.
- [React Three Rapier](https://pmndrs.github.io/react-three-rapier/): integración de Rapier WASM con React Three Fiber.
- [Colyseus — documentación](https://docs.colyseus.io/): salas, matchmaking y sincronización con servidor Node.js autoritativo.
- [Colyseus — netcode](https://docs.colyseus.io/netcode): referencia para input autoritativo, timestep fijo, predicción, reconciliación y compensación de latencia.

Las URLs sirven para resolver APIs y versiones durante P0. No usar `latest` sin registrar el lockfile. La existencia de una función en documentación reciente no demuestra que esté disponible en la versión fijada del proyecto.

---

## 30. Ampliación aprobada: personajes, escenarios y primer desarrollo multijugador

### 30.1 Selección de personaje

- La pantalla de entrada muestra tres personajes originales: **Kira**, **Vektor** y **Atlas**.
- Cada uno tiene silueta, casco, chaleco, hombreras y colores secundarios distintos. La selección inicial es estética; no altera daño, velocidad ni hitbox.
- El jugador elige alias, personaje y escenario antes de entrar. El servidor valida la elección y asigna el equipo de forma equilibrada.
- La selección se transmite a todos y determina el avatar 3D remoto. El jugador ve su propio equipo y personaje en HUD.
- Un cambio posterior de personaje solo se aplica al entrar a otra sala o en una fase de selección futura; no permite cambiar hitbox en mitad del combate.

### 30.2 Escenarios WebGL procedurales

- Primera entrega: **Depósito Delta** y **Terminal Nocturna**.
- Cada mapa tiene plantas, muros, coberturas, cajas, tuberías, escaleras transitables, plataformas elevadas y escondites con entrada real.
- Las piezas se componen con geometrías y materiales de Three.js mediante React Three Fiber. Deben tener siluetas reconocibles: una caja de carga tiene aristas/refuerzos, una cubierta tiene techo y abertura, una escalera tiene peldaños y acceso a plataforma.
- La geometría visible y las colisiones del servidor provienen de la misma definición compartida de mapa. Un muro visible no puede ser atravesable y una abertura visual debe permitir paso.
- Los escondites permiten romper línea de visión y cubrirse de disparos. No conceden invisibilidad por flag.
- Las escaleras elevan realmente al avatar y su cámara; la plataforma debe ser alcanzable y permitir volver a bajar.
- Cada escenario tiene paleta, iluminación y composición propias sin alterar la claridad competitiva.

### 30.3 Primer incremento funcional

Entregar una aplicación React/Vite/Three.js y un servidor de WebSocket con salas independientes por código. Dos navegadores conectados con el mismo código deben verse, votar mapa, moverse y dispararse cuando el anfitrión inicie. El servidor asigna IDs/equipos, valida selección, posición, velocidad, colisiones, cadencia, daño, eliminación y puntos de ronda. Las posiciones se publican en snapshots; el cliente representa al resto con interpolación ligera.

Este incremento usa un protocolo WebSocket pequeño y explícito para poner a prueba juego y mapa. La arquitectura Colyseus de la sección 2 sigue siendo la opción para matchmaking, reconexión y estados de rondas completos; se evaluará su incorporación antes de P4. Si se conserva WebSocket directo, documentar la decisión y cubrir las mismas garantías autoritativas. El primer incremento no se debe etiquetar como partida competitiva completa: compra, dispositivo, utilidades, reconexión y anti-cheat avanzado siguen pendientes.

### 30.4 Pruebas de aceptación del incremento

1. Abrir dos clientes con el mismo código: cada uno ve alias, equipo y modelo seleccionado del otro; al iniciar comparten el mapa votado.
2. Abrir un tercero con otro código: no aparece en la primera sala.
3. Caminar y agacharse junto a cobertura: el servidor impide atravesarla.
4. Subir y bajar la escalera: cámara y avatar cambian de altura sin teletransporte.
5. Entrar al escondite y salir por su abertura: sus paredes bloquean rayos.
6. Disparar a un jugador visible: solo el servidor asigna daño; cobertura bloquea el tiro.
7. Cerrar un cliente: su avatar desaparece para los demás.
8. La aplicación compila, el servidor arranca y no produce errores repetidos.

### 30.5 Estado del primer incremento

La selección de personaje, los modelos procedurales, el movimiento con colisión, la elevación por escaleras y los disparos validados por servidor están implementados. Las salas se identifican ahora por código, el mapa se elige mediante votación y la reaparición se produce entre rondas. `npm test` cubre geometría y una conexión real de tres clientes; `npm run build` valida el cliente. El README contiene las instrucciones para ejecutar la versión local. La calidad visual actual es de **prototipo geométrico**: los modelos no cumplen aún el objetivo de arte final, materiales PBR completos ni animaciones de producción. La comprobación manual de todos los recorridos y el perfilado en equipos de gama baja siguen pendientes.

---

## 31. Lobby multijugador, votación y partidas por rondas

### 31.1 Acceso desde otras máquinas

- El servidor escucha en la interfaz de red y el cliente construye la URL WebSocket a partir del host de la página, salvo que `VITE_WS_URL` indique otro host. Para jugar desde otra máquina en la misma red, abrir el cliente con la IP LAN del equipo servidor y habilitar los puertos del cliente y del WebSocket en el firewall.
- El anfitrión comparte un código de sala corto. Los jugadores ingresan ese código, alias y personaje; el servidor asigna un identificador único. Dos códigos distintos aíslan jugadores y estado. Capacidad inicial: diez jugadores por sala; los equipos se equilibran al entrar.
- La sala presenta participantes, equipos, votos, configuración y estado. Solo el anfitrión puede cambiar la duración y comenzar; si sale, el rol pasa a otro participante. Se invalida un voto al salir.
- El acceso por LAN no equivale a despliegue público. Para Internet se necesitarán WSS, NAT/hosting, autenticación, protección contra abuso y regiones; no exponer el prototipo directamente.

### 31.2 Votación de escenario

- Durante el lobby cada jugador puede votar por Depósito Delta o Terminal Nocturna, y modificar su voto antes del inicio. El servidor cuenta un voto por ID, publica totales y decide por mayoría al iniciar. Un empate usa el voto del anfitrión; si este no votó, se elige Depósito Delta de forma determinista.
- La selección final se anuncia a todos antes de cargar la escena. No se cambia el mapa durante una partida; una revancha regresa al lobby y permite votar de nuevo.

### 31.3 Configuración y puntuación

- El anfitrión configura duración de cada ronda entre 60 y 300 segundos, duración máxima total de la partida entre 5 y 30 minutos y puntos necesarios para ganar entre 1 y 9. Estos valores se bloquean al comenzar la partida.
- Los equipos empiezan con cero puntos. Una ronda termina cuando un equipo elimina a todos los rivales. Ese equipo obtiene un punto. Si acaba el tiempo, gana el equipo con más sobrevivientes; si empatan, la ronda no da puntos.
- No hay reaparición dentro de una ronda. Tras una pausa breve, todos reaparecen con salud completa en su zona y empieza la siguiente. Termina la partida al alcanzar el objetivo de puntos, el límite total de tiempo o un máximo de `2 × puntos necesarios − 1` rondas. El reloj total trunca la última ronda; no asigna un punto por una ronda inconclusa. Si nadie alcanza el objetivo, gana el equipo con más puntos; el empate se anuncia explícitamente.
- El servidor es la única fuente de fase, reloj, marcador, eliminación y cambio de ronda. El cliente representa el tiempo del servidor y no puede adjudicar puntos localmente. Al desconectarse un jugador, se reevalúa la condición de victoria; una sala sin dos equipos vuelve al lobby al finalizar la ronda.

### 31.4 Pruebas de aceptación

1. Dos máquinas en la misma LAN abren la URL del cliente con IP del anfitrión y entran con el mismo código; se ven en el lobby y en el mapa.
2. Un código diferente mantiene aislados jugadores, votos y puntuación.
3. Cada jugador tiene un voto; cambiarlo o desconectarse actualiza los conteos. El empate se resuelve con la regla documentada.
4. Solo el anfitrión puede cambiar duración y puntos objetivo e iniciar con integrantes en ambos equipos.
5. Una eliminación total y un timeout cambian de ronda y puntúan según regla; un eliminado no reaparece antes de la próxima ronda.
6. El marcador y la fase coinciden en todos los clientes; el resultado final se congela y se puede volver al lobby.

### 31.5 Estado actual y siguientes pruebas

El servidor y la interfaz ya implementan acceso por código, anfitrión transferible, votos de mapa, ajustes de ronda y duración total, inicio condicionado a dos equipos, reloj autoritativo, puntos por ronda, resultado y revancha. Las pruebas automatizadas comprueban aislamiento, voto empatado, permisos de configuración, inicio y resultado al desconectarse el rival. Falta probar físicamente dos computadores en la red del usuario y medir latencia, estabilidad y rendimiento durante una partida completa.

---

## 32. Presupuesto de render y adaptación de pantalla

- Menú y lobby deben permitir scroll vertical en ventanas bajas y móviles; botones de entrada, inicio y salida deben permanecer alcanzables. La escena de juego ocupa la ventana y no desplaza el documento.
- Las piezas estáticas repetidas del mapa se renderizan mediante `InstancedMesh` agrupado por acabado. La colisión continúa usando la definición compartida del mapa; el agrupamiento visual no altera hitboxes ni rutas.
- Los avatares remotos agrupan sus piezas de cuerpo, brazos y piernas en mallas instanciadas por segmento. Los segmentos conservan sus animaciones y la selección de personaje sigue distinguiendo casco, visor y color.
- La vista previa de selección usa render bajo demanda y DPR 1. El juego usa DPR 1 inicial; reducirlo automáticamente solo tras medir una caída real de rendimiento con la pestaña activa y preservar legibilidad del enemigo.
- En desarrollo, `window.__strikePerf` informa FPS, llamadas de dibujo y triángulos aproximados. Medir con una pestaña activa, resolución anotada, equipo identificado y número de clientes renderizados. Registrar p50 y p95 de tiempo de cuadro en pruebas posteriores; una captura aislada no demuestra estabilidad competitiva.
- Prueba local inicial: Intel HD Graphics 520, ventana 1100×700, un cliente WebGL activo y otro cliente de red sin escena; 60 FPS y 14 llamadas de dibujo observadas. Repetir con dos y diez clientes gráficos, equipos de gama baja y sesiones completas antes de fijar el presupuesto definitivo.
