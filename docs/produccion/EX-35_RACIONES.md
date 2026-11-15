# EX-35 · Ración sellada OBJ-057

Envase original de 0.20 × 0.12 × 0.04 m, 788 triángulos (presupuesto 800), un mesh y un atlas PBR 512 con cuatro mapas. La malla cerrada tiene volumen, pliegues de transporte, bordes prensados y muesca real de apertura. No se agregó óxido a un alimento de producción reciente. Las dos caras llevan impresión original; lote ficticio EVA-R046-09, producción 4046-09 y consumo antes de 4047-09, coherentes con el año de la campaña. Son decisiones de arte, no datos alimentarios reales.

Fuente reproducible en `SourceArt/Scripts/build_ration_ex35.py`, imágenes en `prepare_ration_ex35.py`, fuente `.blend` con imágenes empaquetadas y exportación FBX. La validación de la malla registra cero bordes no manifold. La verificación de ejes se realiza sobre muestras reales de vértices importados. No se usa material transparente ni una etiqueta flotante sobre la envoltura: la impresión se hornea sobre las superficies del paquete.

## Integración

RationReview sustituye la presentación de seis pickups: R01 en S1, R02/R03 en S2, R04/R05 en S3 y R06 en S4. Conserva componentes Pickup/PersistentEntity, GUID, cantidad de una unidad y reglas de inventario. El nuevo hijo visual se desactiva con el pickup al recogerlo. Un único BoxCollider a escala real permite la interacción; el prefab visual no lleva collider ni audio propio. RegionSceneBuilder incluye la integración al regenerar sectores.

Se conserva el soporte existente identificado por `Support_<ID>`. El paquete queda con su punto inferior sobre ese soporte. La captura inicial descubrió que la antigua jerarquía Visual todavía estaba activa, aunque el renderer raíz se había desactivado. Se corrigió en los seis puntos y se añadió una aserción que exige que todos los renderers ajenos al modelo nuevo estén apagados. Las capturas `regional_R01.png` y `regional_R01_access.png` documentan el fallo; `regional_R01_fixed.png` muestra el estado corregido.

## Validación

Suite completa **104/104 Edit Mode**, trabajo `87981beca0ac41e991f35958b5552627`, 3.2318284 s, después de corregir la presentación antigua. Cuatro pruebas regionales verifican seis identidades/cantidades, dimensiones, contacto con soporte, hitbox accesible desde arriba, presupuesto de malla, textura 512 y ausencia de geometría antigua visible. XML nativo en `SourceArt/_evidence/EX-35/edit-mode-tests.xml`. Capturas Unity frontal, reverso y montaje R01 revisadas. No se ejecutó una nueva suite Play Mode; no se modificó la lógica de curación.

Build Windows **EX35-Rations: Succeeded**, 351.6 MB, 16.76 s, cero errores y una advertencia, después de corregir la presentación antigua. Registro en `evidencia/build_EX35-Rations.json`. Segunda aplicación vacía; REG-S1 sin cambios pendientes.

## Pendientes de aceptación

Falta el clip específico de abrir/usar la ración y el sonido breve de envoltura. Actualmente ViewmodelController selecciona Arms_Syringe para toda curación, incluida la ración: el modelo de pickup no resuelve ese defecto del gesto. Los soportes de bloque deben sustituirse por muebles definitivos; faltan recorrido de jugador y comprobación con iluminación final. Estado Integrado, aceptación no probada. El objetivo de todos los modelos continúa activo.
