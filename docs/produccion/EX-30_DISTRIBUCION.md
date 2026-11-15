# EX-30 · Cuadro de distribución y autorización A

OBJ-033 construido según ficha: chapa plegada, zócalo, doce contactores recientes sobre tres carriles, conductores y canaletas interiores, tres prensaestopas superiores, compartimento de control con manija, botón y dos indicadores. Dimensiones de la fuente: 1.4 × 0.3 × 1.8 m. Una malla y un atlas PBR 1024, 2948 triángulos; los dos indicadores de Unity añaden 32, para **2980 triángulos** en el conjunto. Los paneles son estáticos; la ficha exige el cambio de indicador, no apertura de puertas.

El primer atlas dejaba el rótulo borroso. Se reservaron trece islas UV para el cartel y los doce identificadores de módulo, manteniendo las demás islas en un área separada. Se volvieron a generar los cuatro mapas y el mapa combinado de Unity. El cartel ocupa aproximadamente 266 × 233 píxeles del atlas y es legible en las capturas finales sin aumentar la resolución.

## Integración

DistributionPanel_EX30 queda en REG-S2, patio técnico, origen (116,-8,3.1505), giro Y=180. Apoya en el suelo y deja la trasera a 0.5 mm del muro sur encontrado por raycast. La carcasa tiene un collider simple y un obstáculo de navegación con carving. El botón está a 1.14 m sobre el suelo y su caja sobresale del housing, de modo que el rayo de interacción encuentra el control primero.

MECH-PANEL-A conserva identidad, PERMISO_A y precarga REG-C2. La operación original habilita D14 y completa O05; ServicePanelVisual solo refleja el estado y no concede permisos ni repite sonidos/eventos. La energía permanece verde y la autorización pasa de naranja a verde. Al restaurar el registro se recupera ese estado.

La reimportación de un prefab puede eliminar la referencia de escena a su componente de presentación. Apply repara expresamente el vínculo con el mecanismo hijo y registra la modificación del prefab. Se comprobó guardando y recargando S2, y la siguiente aplicación no produce cambios. RegionSceneBuilder incluye el montaje al regenerar S2.

## Validación

- Importación: 2948 triángulos, una submalla, ejes con error máximo cero, medidas 1.4 × 1.8 × 0.3 en Unity.
- Capturas neutral, autorizada y regional revisadas; rótulo legible y estados de indicador distintos. Evidencias en `SourceArt/_evidence/EX-30/OBJ-033_CuadroDistribucion`.
- Sin penetraciones de carcasa superiores a 2 mm contra WorldStatic. Cápsula de aproximación de radio 0.3 m y altura 1.7 m libre delante del control. Esto no sustituye un recorrido completo en primera persona.
- DistributionPanelTests pasa con escena recargada: alcance de control, referencia a MECH-PANEL-A, altura, indicador, permiso D14, O05, activación única y restauración sin repetir eventos.
- **84/84 Edit Mode**, trabajo `258ebe3f0a6440fe809de214dff9e472`, 1.9119 s; XML guardado en EX-30. No se ejecutó nueva suite Play Mode.
- Build Windows **EX30-Distribution: Succeeded**, 317.86 MB, 21.72 s, cero errores y dos advertencias. Registro en `evidencia/build_EX30-Distribution.json`.

## Pendientes

Conexión visible de los prensaestopas hacia equipos y luminaria del patio técnico, desgaste localizado por uso en la manija, mezcla sonora final del contactor/compuerta y recorrido con jugador. Los módulos recientes y su cableado interior ya están modelados; no se da por resuelta la distribución exterior por la presencia de canaletas interiores. Estado **Integrado**, no Conforme. Continúa el objetivo global.
