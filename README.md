# Mantenimiento Strike — primer incremento jugable

Prototipo multijugador original en navegador, desarrollado a partir de [los requisitos](./PLAN_REQUISITOS_MANTENIMIENTO_STRIKE.md). Usa React, TypeScript, Three.js, React Three Fiber y un servidor Node.js con WebSocket. Los personajes y escenarios son modelos procedurales WebGL; aún no son arte final.

## Ejecutar

Requiere Node.js 22 o posterior. Desde la raíz del repositorio:

```bash
npm ci
npm run dev
```

Abrir `http://localhost:5173` en el anfitrión. Para entrar desde otro computador de la misma red, abrir `http://IP_LAN_DEL_ANFITRIÓN:5173/?room=CÓDIGO`; si el firewall lo solicita, permitir los puertos TCP `5173` y `2567`. El cliente utiliza el host de la página para WebSocket; si la topología es distinta, establecer `VITE_WS_URL=ws://IP_DEL_SERVIDOR:2567` al iniciar Vite. Los participantes comparten el mismo código de sala. Cada sala admite hasta diez jugadores. En modo por equipos, el servidor asigna inicialmente un equipo equilibrado y cada jugador puede cambiarlo en el lobby, con un máximo de cinco por equipo. Esta configuración está pensada para LAN de confianza, no para exponerla directamente a Internet.

`npm run build` valida TypeScript y genera el cliente. `npm test` ejecuta las pruebas de geometría, disparos y sala multijugador. `npm run start` inicia solo el servidor.

## Controles y alcance actual

WASD mueve, ratón apunta, clic dispara, mantener F activa la carrera, Shift agacha, Espacio salta y Escape libera el cursor. El botón **PANTALLA COMPLETA** amplía el juego. Se puede elegir entre Kira, Vektor y Atlas; su diferencia es visual. En el lobby se ve quién participa, se vota entre Depósito Delta y Terminal Nocturna, y el anfitrión elige entre **por equipos** y **todos contra todos**, además de configurar la duración y los puntos necesarios para ganar. En equipos se juegan rondas sin reaparición durante la ronda y cada jugador elige Intrusos o Custodios. En todos contra todos, cualquier otro jugador es rival, cada baja suma un punto individual y el eliminado reaparece a los tres segundos hasta que alguien alcance la meta o se agote el tiempo. Los mapas tienen coberturas, escondites techados, escaleras transitables y pasarelas. El servidor valida movimiento, salto, colisiones, disparos y daño por zona del cuerpo.

Este incremento demuestra el circuito multijugador y las rondas por puntos. Aún faltan objetivo táctico más allá de la eliminación, armas múltiples, munición, economía, sonidos, animaciones de calidad final, arte modelado de alta fidelidad, predicción/reconciliación de red, reconexión y despliegue público. Las decisiones de producción y criterios posteriores permanecen en el documento de requisitos.

## Rendimiento y pantallas pequeñas

El menú y el lobby se desplazan verticalmente cuando su contenido supera la altura de la ventana; el área de juego permanece fija. La vista previa del personaje dibuja solo cuando cambia, y la geometría estática de cada mapa se agrupa en tres mallas instanciadas. Las piezas de cada avatar remoto también se agrupan, conservando movimiento independiente de brazos y piernas. En desarrollo, `window.__strikePerf` muestra FPS, llamadas de dibujo y triángulos aproximados del último segundo. En una prueba local con Intel HD Graphics 520, un cliente WebGL activo a 1100×700 y otro cliente conectado sin renderizar, se observaron 60 FPS y 14 llamadas de dibujo; este dato no sustituye pruebas en otros equipos o con diez jugadores.
