# EX-29 · Tablero antiguo de servicio

OBJ-009 modelado desde su ficha: carcasa hueca de chapa, placa aislante, dos carriles, terminales, cableado protegido, reparación con cinta, puerta abisagrada, manija, palanca independiente, indicadores de energía local/enlace y nota de Mara. Dimensiones importadas 0.8 × 1.1 × 0.25 m en ejes Unity. Tres mallas, 1452 triángulos, atlas PBR 1024; pivotes de puerta y palanca conservados con error de coordenadas cero. Dos módulos OBJ-010 añaden 720 triángulos y reutilizan su atlas 512. Los dos indicadores añaden 32 triángulos y material plano sin textura: total de la composición 2204 triángulos, dos sets de textura.

El prefab tiene cinco cajas de carcasa y una caja de puerta; el frente permanece abierto. La hoja gira 108 grados en 0.9 s mediante HingedCabinet, con su detección de obstrucción y persistencia. ServicePanelVisual sigue el permiso existente y mueve la palanca 55 grados en 0.5 s; congela su avance con delta de tiempo cero y recupera la pose al hidratar el estado. La animación vive en Unity; el FBX contiene mallas y pivotes, sin clips.

## Montaje

ServicePanel_EX29 se ancla al muro este de S1, encontrado por raycast a X=34. Su origen es (33.8995,-17.45,6), giro Y=90, trasera a 0.5 mm del muro. La carcasa empieza 0.55 m sobre el suelo. El placeholder M018_tablero se retira solo si no contiene lógica.

MECH-LEVER-S1 conserva su componente, identificador, PERMISO_SERVICIO y precarga REG-C1; se reubica dentro del tablero. La caja de interacción queda detrás de la puerta. DOC-02 conserva GUID, cantidad e identidad, se coloca sobre el papel interior y pierde únicamente el soporte y la malla provisional. Un extracto de DocumentLibrary está impreso en el atlas; el texto íntegro sigue en el archivo de documentos existente. El papel permanece físicamente después de archivar la nota.

El gabinete tiene identidad persistente CAB-SERVICE-S1 independiente del permiso. La alimentación local aparece verde; el enlace pasa de naranja a verde tras la operación. Solo Mechanism concede permisos, reproduce SND-LEVER y emite el ruido lógico ya definido; el componente visual no repite esos efectos. Las futuras regeneraciones de S1 aplican el montaje y su segunda aplicación es vacía. Los gabinetes eléctricos murales quedan excluidos del obstáculo de suelo genérico de CabinetPlacement.

## Evidencia

- Fuente `SourceArt/Blender/OBJ-009_TableroAntiguo.blend`; receta `SourceArt/Scripts/build_service_panel_ex29.py`.
- FBX, material y prefab en las carpetas Art/Prefabs de Unity. Informe de importación y ejes en `SourceArt/_evidence/EX-29/OBJ-009_TableroAntiguo`.
- Captura neutral, captura de S1 y hoja de contacto de puerta a 0/0.45/0.9 s revisadas: giro rígido, bisagra estable, materiales conservados y acceso interior.
- ServicePanelTests: 2/2. Verifica primer impacto de rayos con puerta cerrada/abierta sobre control y nota, identidad de DOC-02, activación única, pausa y restauración sin repetir eventos.
- Suite completa Edit Mode: **83/83**, trabajo `db3ba1021b1c493a8f165e840c3ff7a4`, 1.8604 s; XML guardado en EX-29. La prueba de gabinetes de campaña incluye ahora cuatro gabinetes en S1. No se ejecutó una nueva suite Play Mode.
- Build Windows EX29-ServicePanel: **Succeeded**, 314.36 MB, 39.09 s, cero errores y 55 advertencias. Registro en `evidencia/build_EX29-ServicePanel.json`.
- Reaplicación sin cambios, escena S1 sin cambios pendientes y consola sin errores al cerrar esta entrega.

## Pendientes de acabado

Ruta física del cable de red desde el tablero hasta el contacto de D06 (actualmente el cable termina dentro del gabinete); polvo y marcas de dedos localizados; revisar el manchado demasiado difuso del interior de la puerta; mezcla final de relé/contacto y lectura con linterna a distancia de juego. La colocación cambia respecto al bloque inicial, donde nota, palanca y gabinete estaban separados varios metros; falta recorrido completo con jugador en primera persona. OBJ-009 y OBJ-010 están **Integrados**, no declarados Conforme. OBJ-033 sigue pendiente. El objetivo global continúa activo.
