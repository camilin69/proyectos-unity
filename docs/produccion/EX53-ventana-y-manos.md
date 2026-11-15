# EX53 — Ventana y manos

- Sustituye el inicio en pantalla completa de EX52 por una ventana de 1280 × 720, redimensionable y maximizable desde Windows. La resolución nativa ya no se fuerza al abrir.
- Pantalla completa sigue siendo una opción explícita en Ajustes. La preferencia `esn.borderless` evita heredar la activación de EX52.
- Corregida la lateralidad de los antebrazos después de evaluar la animación: mano izquierda a la izquierda, derecha a la derecha y pulgares hacia dentro. Las posiciones transversales se aplican sin acumular desplazamientos; los anclajes de armas siguen a sus huesos.
- Revisión visual en reposo y con pistola/linterna: `Captures/EX53/hands-inward.png` y `hands-equipped.png` dentro del proyecto Unity.
- PlayMode: 4/4 aprobadas, job `4bd07d0e0ef44cef86e81b3e1de662b9`. Incluye aserciones nuevas de lateralidad y pulgares en reposo, además de combate y jeringa.

Ejecutable: `Builds/EX53-WindowedHands/EsneiderProtocoloLazaro.exe`.
No se ha medido el rendimiento de la ventana maximizada en el equipo del usuario.
