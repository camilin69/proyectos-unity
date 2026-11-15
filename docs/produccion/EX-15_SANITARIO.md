# EX-15 · Modelos sanitarios

Tres fuentes Blender nuevas con UV, cuatro mapas PBR 1024, FBX y prefab de un submesh. Se usaron las skills de modelado, materiales, exportación y revisión visual de Blender con el transporte MCP aislado 9877; integración y comprobaciones en Unity MCP.

| Modelo | Triángulos | Entrega |
|---|---:|---|
| OBJ-005 Depósito criogénico | 3388 | Tres unidades en M003/S1 |
| OBJ-006 Carro sanitario | 5768 | Sustituye Support_PICK-F01/S1 |
| OBJ-014 Cortina sanitaria | 15800 | Prefab validado, sin montaje regional todavía |

El depósito mide 0.65 × 0.6506 × 1.6 m, con patas, válvula, manómetro, etiqueta curva y manchas bajo la unión. Se eliminaron 80 triángulos degenerados de los polos; fuente e importación coinciden. Su puerto permanece tapado para servicio: falta conectar el conjunto a la instalación según la ficha.

El carro mide 0.87 × 0.53 × 0.90 m, próximo al objetivo 0.90 × 0.55 × 0.90. Tiene cuatro ruedas con horquillas/ejes, dos bandejas, marco abierto, asa y rayas localizadas. Conserva PICK-F01, tipo Flashlight y su interacción. El mínimo de la malla de la linterna queda a 0.0005 m de la bandeja. Falta incorporar el dibujo del sol de la ficha y revisar el desgaste de cerca.

La cortina mide 2 m de ancho y aproximadamente 2.16 m de alto visible; tiene grosor, pliegues variables, franja inferior oscura, trece ganchos y riel. El origen deja 4.5 cm de separación inferior para el montaje. Falta costura/refuerzo superior, mayor irregularidad del borde húmedo, revisión de LOD y montaje contra techo real; no tiene animación ni collider en la tela. El único collider pertenece al riel.

## Validación

- FurnitureReview verificó topología, mapas y transformación de coordenadas de los tres modelos, con registros individuales en SourceArt/_evidence/EX-15.
- Revisión visual de los tres previews Unity, el carro con linterna y los depósitos dentro de S1. Se detectó y retiró solamente el antiguo S1_CoolantTank de EX10 superpuesto a M003. MedicalPlacement conserva esta sustitución al regenerar S1 después de S1VisualPass.
- Rayos de comprobación libres bajo la bandeja y a través de la tela; contacto de linterna registrado en open-area-rays.txt y pickup-contact.txt.
- Suite existente 47/47 Edit Mode, job ba331a308136433c930ec3fa09e1e69f. Comprueba regresiones anteriores; las comprobaciones específicas EX15 son las anteriores, no nuevos casos de esa suite. La última eliminación del decorado superpuesto se verificó directamente y mediante captura.
- Build EX15-Medical: Succeeded, 238 MB, 19.96 s, cero errores, una advertencia del paquete com.unity.pipeline por RuntimePipelineConfig ausente. Informe en docs/produccion/evidencia/build_EX15-Medical.json. La build contiene cambios locales no identificados únicamente por el SHA base.

No se repitió Play Mode ni se midió navegación/rendimiento. La captura con F conserva la implementación y evidencia EX12. Los estados son Integrado/Prefab validado, no Conforme; el catálogo completo sigue pendiente y la auditoría metálica anterior aún señala quince assets antiguos por reparar.

Reproducción: build_medical_props_ex15.py, build(id), render(id), finish(id) mediante Blender MCP; FurnitureReview.Integrate/Capture y MedicalPlacement.ApplyExisting mediante Unity MCP. Evidencia en SourceArt/_evidence/EX-15.
