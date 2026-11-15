# EX54 — Inventario de nueve casillas y puertas

## Comportamiento

- Nueve casillas numeradas siempre visibles. Los tipos de objetos se agregan por orden de recogida; una pila agotada conserva su número. Los documentos siguen en su interfaz de lectura.
- Teclas 1–9 y rueda seleccionan casillas, incluidas las vacías. Borde amarillo y nombre de la selección sobre la barra. Recoger otro objeto no reemplaza la selección.
- Clic izquierdo usa el objeto seleccionado: ataque con armas, consumo de la cura elegida. Clic derecho enciende/apaga la linterna, que permanece en la mano izquierda al recogerla. F se conserva exclusivamente para escapar de la red.
- Armas, raciones, jeringas y cajas de munición tienen presentación en la mano derecha. Seleccionar la casilla de linterna deja libre la derecha; no duplica la linterna.
- Orden y selección incluidos en el checkpoint. Guardados antiguos reconstruyen un orden estable a partir de los objetos que tenían; su orden histórico no estaba registrado.
- Vida expresada como porcentaje del máximo: 90/90 HP se muestra como 100%.

## Puertas

- Las puertas bloqueadas muestran la condición pendiente al apuntarlas. D06 exige la palanca de servicio; la autorización no se elimina.
- El clip de las puertas animadas se mantiene evaluable en ambos extremos y fuera de cámara. Su obstáculo de navegación se desactiva al terminar de abrir.
- Comprobación manual en S1: D04 y D06 abiertas dejan pasar una cápsula de radio 0.3 m, sin colisionar con geometría estática ni hojas. La inspección aislada de S1 no carga el corredor C1 (el fondo exterior de las capturas no representa una partida con streaming).

## Evidencia

- Pruebas PlayMode: orden, selección de casilla 9, uso de ración sin gastar jeringa, anclajes de ambas manos, snapshot JSON/restauración, combate, jeringa, persistencia y escape de red.
- Regresión de puertas: abrir/cerrar/abrir; operar la palanca y comprobar paso por D04/D06.
- Capturas en el proyecto Unity: `Captures/EX54/hotbar-nine-pistol.png`, `ration-upright.png`. La caja de munición se redujo después de la revisión para ocupar menos pantalla.
- Una ejecución inicial encontró un fallo de actualización del arma seleccionada, ya corregido, y estado heredado entre pruebas de puertas, ya aislado. Una inicialización de pruebas se quedó huérfana y se reinició; no se contó como validación.

- Ejecución general: 13/13 aprobadas, job `2f3d4fe3bc504feaabf3194c10ecfcc3`. Tras ampliar la comprobación de paso y ajustar los consumibles, regresiones finales: 2/2 aprobadas, job `694675a8c29c48c7ada192ef2bb36ad4`. Ejecuciones sin pruebas descubiertas se excluyeron.

Ejecutable: `Builds/EX54-Inventory/EsneiderProtocoloLazaro.exe`.
