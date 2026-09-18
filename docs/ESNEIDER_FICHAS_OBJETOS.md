# Esneider: fichas individuales de objetos y montaje

Anexo A · Versión 1.0 · 17 de septiembre de 2026.

[Documento maestro y biblia de arte](ESNEIDER_BUNKER_GDD.md).

Estado: especificación original; ningún objeto queda certificado como modelado por aparecer aquí. Medidas, materiales y técnica son objetivos a verificar con hardware, software y cámara reales. Las 80 fichas cubren el catálogo OBJ del documento maestro; no incluyen 80 modelos nuevos encima de ese catálogo. Cada ficha tiene decisiones específicas de construcción, superficie, movimiento, colisión, sonido, montaje y aceptación. Personajes y armas se detallan adicionalmente en las secciones 35–38 y 63–65 del maestro.

## Contrato común de entrega

- Fuente .blend preservada, export FBX comprobada, texturas fuente/runtime y prefab Unity.
- IDs estables; pivot, escala métrica, UV y materiales documentados. No instanceID como identidad persistente.
- Versiones de Blender/Unity y packing de mapas registrados; shaders reconstruidos según pipeline real.
- High/low, bake, rig y LOD cuando aporten valor. No exigir escultura y armadura a una hoja de papel estática.
- Colliders simples por función; no geometría render completa como collider por defecto.
- Captura bajo luz neutra y luz de juego; clips revisados en movimiento cuando exista animación.
- Estado: Pendiente / Blockout / En producción / Revisar / Integrado / Conforme. Solo Conforme cuando haya evidencia.
- Procedencia/licencia de recursos externos y autoría de los originales. No afirmar enlaces compartidos inexistentes.

## Catálogo de fichas

### OBJ-001 · Criocámara Lázaro

**Función:** Apertura animada y origen de Esneider.

**Construcción exigida:** Base estructural, tapa, vidrio curvo, bisagras, juntas, tubos y panel.

- **Medidas objetivo:** 2.4 × 1.1 × 1 m.
- **Materiales y respuesta visual:** Acero pintado, goma, vidrio y polímero interior.
- **Desgaste con causa:** Pintura levantada en marco; junta aún mantenida; condensación bajo tapa.
- **Movimiento y estados:** Seguro libera, junta despega, tapa abre; mano deja huella.
- **Colisión e interacción:** Base y marco sólidos; espacio libre al levantarse; tapa no aplasta.
- **Firma sonora:** Válvula, seguro, motor, roce y cierre final.
- **Montaje y relaciones:** Tubos al manifold y energía al núcleo; holgura de tapa con pared.
- **Prueba específica de acabado:** Ver huella, interior y marco de cerca; salir sin quedar atrapado.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-002 · Cámara vacía dañada

**Función:** Historia de otros sujetos, variante no nuevo modelo académico.

**Construcción exigida:** Mismo sistema, tapa deformada y lecho visible.

- **Medidas objetivo:** Misma escala que OBJ-001.
- **Materiales y respuesta visual:** Materiales compartidos, vidrio roto solo en variante concreta.
- **Desgaste con causa:** Daño focal y lecho hundido; marca del sujeto anterior.
- **Movimiento y estados:** Tapa atascada intenta abrir una vez; después queda estable.
- **Colisión e interacción:** Fragmentos importantes sólidos; astillas pequeñas decorativas.
- **Firma sonora:** Motor fallido corto y metal final; sin loop infinito.
- **Montaje y relaciones:** Una unidad focal entre cámaras intactas y abiertas.
- **Prueba específica de acabado:** Distinguir daño de simple recolor; no vidrios flotando ni bordes sin espesor.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-003 · Consola de preservación

**Función:** Tiempo transcurrido y ficha.

**Construcción exigida:** Pantalla, botones, rejilla, tornillería y panel de servicio.

- **Medidas objetivo:** 0.7 × 0.45 × 1.2 m.
- **Materiales y respuesta visual:** Polímero sanitario, pantalla y metal de montaje.
- **Desgaste con causa:** Teclas usadas, polvo en borde y mantenimiento en conector.
- **Movimiento y estados:** Pantalla cambia diagnóstico a duración; botón responde una vez.
- **Colisión e interacción:** Housing simple; pantalla no bloquea interacción por trigger extra.
- **Firma sonora:** Click, relé tenue y ventilador localizado.
- **Montaje y relaciones:** Pantalla orientada a humano de pie junto a cámara.
- **Prueba específica de acabado:** Leer nombre y 2000 años desde cámara real sin texto quemado.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-004 · Unidad térmica

**Función:** Explica energía/mantenimiento de cámara.

**Construcción exigida:** Radiador, compresor ficticio, aislantes y mangueras.

- **Medidas objetivo:** 1.2 × 0.65 × 1 m.
- **Materiales y respuesta visual:** Metal, aislante, goma y aletas oscuras.
- **Desgaste con causa:** Condensación en conexión, no óxido sobre aislante.
- **Movimiento y estados:** Ventilación leve; ninguna pieza atraviesa cubierta.
- **Colisión e interacción:** Caja principal y salientes grandes; sin collider por aleta.
- **Firma sonora:** Compresor bajo con punto real de emisión.
- **Montaje y relaciones:** Mangueras a cámaras; rejillas con salida plausible de aire.
- **Prueba específica de acabado:** Seguir conexión y reconocer compresor; comprobar normal de aletas con linterna.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-005 · Depósito criogénico

**Función:** Volumen de fondo; no tubo liso.

**Construcción exigida:** Cilindro con patas, válvula, dial y soporte.

- **Medidas objetivo:** 0.65 m diámetro × 1.6 m alto.
- **Materiales y respuesta visual:** Acero pintado, metal de válvula y goma.
- **Desgaste con causa:** Manchas verticales desde unión y etiqueta envejecida.
- **Movimiento y estados:** Dial fijo; válvula estática salvo interacción explícita.
- **Colisión e interacción:** Cilindro simplificado y soporte; no estorba único paso.
- **Firma sonora:** Sin loop propio; sonido de contacto si dinámico.
- **Montaje y relaciones:** Patas apoyadas, brida y tubo con destino.
- **Prueba específica de acabado:** Válvula, soporte y grosor distinguen tanque de cilindro de color.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-006 · Carro sanitario

**Función:** Soporte de linterna.

**Construcción exigida:** Chasis, ruedas, bandejas, asa y piezas móviles.

- **Medidas objetivo:** 0.9 × 0.55 × 0.9 m.
- **Materiales y respuesta visual:** Acero esmaltado, goma y bandejas metálicas.
- **Desgaste con causa:** Asa pulida, rayas en bandeja, ruedas usadas.
- **Movimiento y estados:** Ruedas orientadas a apoyo; carro estático en hallazgo.
- **Colisión e interacción:** Collider de marco/bandeja grande, no tornillería.
- **Firma sonora:** Roce de pickup y contacto opcional; no vibración permanente.
- **Montaje y relaciones:** Linterna apoyada con lente/grip visibles; fuente de luz cercana.
- **Prueba específica de acabado:** Mirar debajo y ver dibujo del sol montado sobre soporte real.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-007 · Armario de preparación

**Función:** Ropa/archivo/ración.

**Construcción exigida:** Puertas con espesor, bisagra, manija y interior.

- **Medidas objetivo:** 1 × 0.5 × 1.9 m.
- **Materiales y respuesta visual:** Chapa pintada, goma y metal de bisagra.
- **Desgaste con causa:** Puño/manija usados, polvo superior, interior protegido.
- **Movimiento y estados:** Puerta abre con pivot real si contiene pickup.
- **Colisión e interacción:** Cuerpo y puerta; comprobar obstrucción y acceso interior.
- **Firma sonora:** Bisagra y latch cortos con fin de acción.
- **Montaje y relaciones:** Repisas y prendas apoyadas; ancho interior compatible con puerta.
- **Prueba específica de acabado:** Abrir y mirar interior sin hueco negro ni pickup atravesando repisa.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-008 · Banco industrial

**Función:** Descanso visual y composición.

**Construcción exigida:** Patas, asiento con desgaste y fijación.

- **Medidas objetivo:** 1.4 × 0.45 × 0.45 m.
- **Materiales y respuesta visual:** Metal pintado y asiento de goma/madera elegida.
- **Desgaste con causa:** Borde de asiento usado, patas húmedas cerca del suelo.
- **Movimiento y estados:** Sin animación; Esneider no necesita sistema de sentarse.
- **Colisión e interacción:** Banco sólido, piernas simplificadas.
- **Firma sonora:** Contacto de metal solo si se mueve por evento.
- **Montaje y relaciones:** Junto a muro/refugio, con espacio humano para piernas.
- **Prueba específica de acabado:** Patas apoyadas y altura humana al comparar manos y cámara.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-009 · Tablero eléctrico antiguo

**Función:** Palanca tutorial y nota escondida.

**Construcción exigida:** Gabinete, bisagra, módulos, cableado y etiquetas.

- **Medidas objetivo:** 0.8 × 0.25 × 1.1 m.
- **Materiales y respuesta visual:** Chapa, aislantes, cobre protegido y plástico.
- **Desgaste con causa:** Polvo dentro, dedos sobre palanca, reparación de Mara.
- **Movimiento y estados:** Puerta de gabinete y palanca separadas; indicadores tras acción.
- **Colisión e interacción:** Collider housing; Interactable no tapa raycast al control.
- **Firma sonora:** Palanca, relé y contacto; ruido no depende del volumen de UI.
- **Montaje y relaciones:** Cable de red hacia contacto del marco de salida.
- **Prueba específica de acabado:** Distinguir red y alimentación; activar anuncia una vez y guarda estado.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-010 · Fusible/módulo

**Función:** Detalle focal del tablero.

**Construcción exigida:** Cuerpo, terminales y texto serial.

- **Medidas objetivo:** 0.08 × 0.04 × 0.12 m.
- **Materiales y respuesta visual:** Cerámica/plástico y terminal metálico.
- **Desgaste con causa:** Etiqueta antigua, contacto usado, sin grunge gigante.
- **Movimiento y estados:** Estático dentro de cuadro; no minijuego inventado.
- **Colisión e interacción:** Sin collider individual salvo pickup definido.
- **Firma sonora:** Click solo si hay interacción; no loop.
- **Montaje y relaciones:** Módulo encaja en soporte con serial legible cercano.
- **Prueba específica de acabado:** No parece ladrillo de color; medidas y terminales tienen función.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-011 · Núcleo sellado ficticio

**Función:** Explicación de reserva energética.

**Construcción exigida:** Carcasa robusta, aislantes y conexión.

- **Medidas objetivo:** 1 × 0.6 × 0.8 m.
- **Materiales y respuesta visual:** Carcasa metálica robusta y aislantes.
- **Desgaste con causa:** Sello íntegro, servicio reciente y marca antigua de empresa.
- **Movimiento y estados:** Indicador estable; no pulso exagerado continuo.
- **Colisión e interacción:** Bloque estático con conexiones decorativas pequeñas.
- **Firma sonora:** Zumbido muy bajo si audible desde cercanía.
- **Montaje y relaciones:** Conexión al sistema local, fuera de línea de combate.
- **Prueba específica de acabado:** Se entiende reserva sellada sin reactor luminoso genérico.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-012 · Escombros de concreto

**Función:** Varilla y obstáculo de física.

**Construcción exigida:** Fragmentos grandes, caras de fractura y armadura.

- **Medidas objetivo:** Grupo de 3–5 m; fragmentos 0.1–0.8 m.
- **Materiales y respuesta visual:** Concreto fracturado y armadura metálica.
- **Desgaste con causa:** Fractura fresca frente a cara exterior envejecida.
- **Movimiento y estados:** Dos piedras leves caen al sacar varilla; resto estático.
- **Colisión e interacción:** Bloques relevantes sólidos; piezas pequeñas ignoran cápsula.
- **Firma sonora:** Dos impactos variados y polvo corto.
- **Montaje y relaciones:** Masa nace de rotura visible; no alfombra aleatoria por toda sala.
- **Prueba específica de acabado:** Fracturas tienen volumen; varilla se puede sacar y ruta no engancha.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-013 · Viga deformada

**Función:** Narrativa estructural.

**Construcción exigida:** Perfil con espesor, doblez y unión rota.

- **Medidas objetivo:** 3–5 m largo, perfil 0.2–0.35 m.
- **Materiales y respuesta visual:** Acero con pintura y metal expuesto.
- **Desgaste con causa:** Doblez, unión rota y óxido localizado.
- **Movimiento y estados:** Estática; no simulación estructural completa.
- **Colisión e interacción:** Collider simple según perfil y camino.
- **Firma sonora:** Sin loop; golpe de varilla da contacto metálico.
- **Montaje y relaciones:** Apoyo coherente entre derrumbe y estructura original.
- **Prueba específica de acabado:** Sección con espesor y causa del daño, sin doblado como goma.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-014 · Cortina sanitaria

**Función:** Oculta parcialmente un volumen.

**Construcción exigida:** Riel, tela, pliegues y borde.

- **Medidas objetivo:** 2 × 2.2 m, pliegues variables.
- **Materiales y respuesta visual:** Tela envejecida y riel de metal.
- **Desgaste con causa:** Borde húmedo bajo, parte superior protegida.
- **Movimiento y estados:** Leve movimiento solo con flujo de aire visible.
- **Colisión e interacción:** Tela no engancha player; riel estático.
- **Firma sonora:** Roce breve muy bajo cuando corresponde.
- **Montaje y relaciones:** Ganchos/riel y caída por gravedad aparente.
- **Prueba específica de acabado:** Pliegues cambian con sujeción y no parecen plano con textura.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-015 · Pulsera Lázaro

**Función:** Identidad y pista.

**Construcción exigida:** Banda, cierre y datos legibles.

- **Medidas objetivo:** Banda 0.02 m de ancho, escala de muñeca.
- **Materiales y respuesta visual:** Polímero flexible y tinta.
- **Desgaste con causa:** Nombre protegido, borde usado, cierre real.
- **Movimiento y estados:** Sigue rig de muñeca; no flota durante recarga.
- **Colisión e interacción:** Sin collider propio en viewmodel.
- **Firma sonora:** Roce de tela integrado, no audio dedicado.
- **Montaje y relaciones:** Mano de Esneider y fichas del programa.
- **Prueba específica de acabado:** Nombre/fecha visibles en gesto concreto sin escalar pulsera artificialmente.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-016 · Placa de emergencia

**Función:** Orientación y nombre de sector.

**Construcción exigida:** Soporte, tornillos y señal original.

- **Medidas objetivo:** 0.45 × 0.3 m, espesor visible.
- **Materiales y respuesta visual:** Chapa pintada y fijación.
- **Desgaste con causa:** Pintura antigua con placa EVA añadida.
- **Movimiento y estados:** Estática.
- **Colisión e interacción:** Sin collider separado si sobre muro.
- **Firma sonora:** Ninguno; no sonido artificial de señalización.
- **Montaje y relaciones:** Altura humana cerca de acceso, tornillos con tamaño plausible.
- **Prueba específica de acabado:** Texto orienta y logo pertenece al mismo mundo que equipo.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-017 · Banco de trabajo

**Función:** Origen de herramientas.

**Construcción exigida:** Estructura, superficie, mordaza y cajones.

- **Medidas objetivo:** 2 × 0.75 × 0.9 m.
- **Materiales y respuesta visual:** Acero, tablero y mordaza metálica.
- **Desgaste con causa:** Zona de trabajo pulida, quemaduras pequeñas cerca de soldar.
- **Movimiento y estados:** Cajón solo si se usa; resto estático.
- **Colisión e interacción:** Volumen principal deja pasar piernas/player.
- **Firma sonora:** Contacto y cajón, sin loops superpuestos.
- **Montaje y relaciones:** Herramientas apoyadas, acceso a mordaza y espacio frontal.
- **Prueba específica de acabado:** No mesa cúbica; patas, uniones y almacenamiento funcionan visualmente.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-018 · Mordaza de banco

**Función:** Silueta de función, prop secundario.

**Construcción exigida:** Base, mandíbula, tornillo y palanca.

- **Medidas objetivo:** 0.35 × 0.18 × 0.2 m.
- **Materiales y respuesta visual:** Metal usado y agarre.
- **Desgaste con causa:** Jaw rayada, tornillo engrasado, base fijada.
- **Movimiento y estados:** Mandíbula opcional por evento autorado.
- **Colisión e interacción:** Sin collider específico si decorativa.
- **Firma sonora:** Clink corto solo si una pieza la usa.
- **Montaje y relaciones:** Atornillada al banco, no sobre el borde sin soporte.
- **Prueba específica de acabado:** Tornillo y palanca explican cómo aprieta; no piezas intersectadas.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-019 · Taladro industrial fijo

**Función:** Fondo de taller.

**Construcción exigida:** Base, columna, cabezal y control.

- **Medidas objetivo:** 0.6 × 0.5 × 1.6 m.
- **Materiales y respuesta visual:** Metal pintado, goma y superficies de herramienta.
- **Desgaste con causa:** Trabajo localizado y etiqueta técnica.
- **Movimiento y estados:** Cabezal quieto o ciclo lento, herramienta no atraviesa mesa.
- **Colisión e interacción:** Bloque simplificado estático.
- **Firma sonora:** Motor localizado solo si está operando.
- **Montaje y relaciones:** Base apoyada y área de trabajo libre.
- **Prueba específica de acabado:** Altura y piezas hacen reconocible máquina industrial.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-020 · Brazo de reparación

**Función:** Animación ambiental lenta.

**Construcción exigida:** Base, joints, actuadores y pinza.

- **Medidas objetivo:** Radio operativo 1.5–2 m.
- **Materiales y respuesta visual:** Acero pintado, actuadores y goma.
- **Desgaste con causa:** Pintura de época humana y joint reciente.
- **Movimiento y estados:** Clip de reparación con pinza/pieza alineadas.
- **Colisión e interacción:** Base sólida; brazo no atrapa cápsula ni ocupa única ruta.
- **Firma sonora:** Servo por joint con eventos limitados.
- **Montaje y relaciones:** Pivot real y herramienta llega al robot en plataforma.
- **Prueba específica de acabado:** Recorrido no atraviesa pieza ni cable; detener clip sigue siendo plausible.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-021 · Plataforma para robot

**Función:** Robot fuera de combate, decoración.

**Construcción exigida:** Raíles, abrazaderas y conexiones.

- **Medidas objetivo:** 2.6 × 1.4 × 0.35 m.
- **Materiales y respuesta visual:** Metal, apoyos de goma y abrazaderas.
- **Desgaste con causa:** Desgaste por cuerpo y ruedas de servicio.
- **Movimiento y estados:** Abrazadera solo si clip lo necesita.
- **Colisión e interacción:** Base sólida; rig decorativo no recibe IA de combate.
- **Firma sonora:** Contacto de soporte durante reparación.
- **Montaje y relaciones:** Conectores llegan a robot; cuerpo cabe sin escalarlo irregularmente.
- **Prueba específica de acabado:** Leer sujeción y mantenimiento, no pedestal vacío.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-022 · Cabeza de Custodio antigua

**Función:** Evolución del diseño corporativo.

**Construcción exigida:** Carcasa, montaje, lente/placa anterior.

- **Medidas objetivo:** 0.3 × 0.25 × 0.35 m.
- **Materiales y respuesta visual:** Polímero, metal y lentes según versión antigua.
- **Desgaste con causa:** Parte protegida limpia, placa sustituida.
- **Movimiento y estados:** Estática sobre soporte; no mirada automática en todas.
- **Colisión e interacción:** Sin collider separado si sobre banco.
- **Firma sonora:** Ninguno fuera de contacto.
- **Montaje y relaciones:** Cable/neck mount visible, póster de modelo anterior cerca.
- **Prueba específica de acabado:** Comparar cara original y actual conserva continuidad de fabricación.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-023 · Bandeja de piezas

**Función:** Historia de mantenimiento.

**Construcción exigida:** Contenedor y tres grupos de piezas plausibles.

- **Medidas objetivo:** 0.45 × 0.3 × 0.07 m.
- **Materiales y respuesta visual:** Bandeja metálica y piezas de juntas.
- **Desgaste con causa:** Aceite en fondo y bordes usados.
- **Movimiento y estados:** Estática.
- **Colisión e interacción:** No collider por tornillo; bandeja parte del banco.
- **Firma sonora:** Clink solo por interacción explícita.
- **Montaje y relaciones:** Tres grupos organizados por función, no nube aleatoria.
- **Prueba específica de acabado:** Piezas tienen espesor y escala que coinciden con robots.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-024 · Locker de seguridad

**Función:** Hallazgo de pistola.

**Construcción exigida:** Puerta, bisagras, cerradura, repisas.

- **Medidas objetivo:** 1 × 0.55 × 1.9 m.
- **Materiales y respuesta visual:** Chapa, bisagras, plástico de soporte.
- **Desgaste con causa:** Apertura/agarre gastados, interior menos oxidado.
- **Movimiento y estados:** Puerta abre y queda; arma pickup independiente.
- **Colisión e interacción:** Cuerpo, puerta y triggers de pickup separados.
- **Firma sonora:** Latch, puerta y equipar.
- **Montaje y relaciones:** Pistola sobre soporte dimensionado; cargadores apoyados.
- **Prueba específica de acabado:** Recoger una vez y ver interior, sin pistola pegada al plano.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-025 · Armario de escopeta

**Función:** Hallazgo de escopeta.

**Construcción exigida:** Soportes y interior dimensionado.

- **Medidas objetivo:** 1.2 × 0.55 × 1.9 m.
- **Materiales y respuesta visual:** Metal pintado y soporte de goma.
- **Desgaste con causa:** Manija usada, marcas de seguridad antigua.
- **Movimiento y estados:** Apertura separada de obtención de escopeta.
- **Colisión e interacción:** Igual a locker, revisar arma larga/puerta.
- **Firma sonora:** Puerta pesada y equipar.
- **Montaje y relaciones:** Soportes dejan ver grip y cartuchos, armas ficticias sin planos.
- **Prueba específica de acabado:** Arma cabe y salida no corta cañón visualmente en pared.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-026 · Gabinete final

**Función:** Suministro CP-06.

**Construcción exigida:** Cuerpo, apertura y reservas separadas.

- **Medidas objetivo:** 1 × 0.5 × 1.8 m.
- **Materiales y respuesta visual:** Chapa, repisas y contenedores.
- **Desgaste con causa:** Mantenimiento relativamente reciente.
- **Movimiento y estados:** Apertura, transacción de recursos y guardado; no rellenar durante intento.
- **Colisión e interacción:** Interactable con collider claro, no bloquea refugio.
- **Firma sonora:** Latch y aviso de checkpoint discreto.
- **Montaje y relaciones:** En CP-06 con stock visible y luz estable.
- **Prueba específica de acabado:** Minimos de munición aplican una vez; snapshot coincide con stock/estado.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-027 · Caja de munición

**Función:** Pickup parcial persistente.

**Construcción exigida:** Tapa, cierre, asa, junta y cartuchos/paquetes.

- **Medidas objetivo:** 0.3 × 0.2 × 0.15 m.
- **Materiales y respuesta visual:** Metal o polímero elegido, etiqueta y junta.
- **Desgaste con causa:** Transporte y apertura en cierre, no óxido en todos los cartuchos.
- **Movimiento y estados:** Tapa estática abierta; estado visual cambia al agotarse.
- **Colisión e interacción:** Pickup parcial, collider no tapa interaction ray.
- **Firma sonora:** Roce/munición breve, sin fanfarria.
- **Montaje y relaciones:** Tipo de munición visible en envase y paquete.
- **Prueba específica de acabado:** Recoger parcialmente conserva resto y no destruye caja injustamente.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-028 · Estantería industrial

**Función:** Ruta de sigilo y cobertura.

**Construcción exigida:** Perfiles, anclajes, repisas y carga.

- **Medidas objetivo:** 2.5 × 0.6 × 2.8 m por módulo.
- **Materiales y respuesta visual:** Perfiles de acero, repisas y cargas.
- **Desgaste con causa:** Roce por carga, polvo arriba, fijaciones.
- **Movimiento y estados:** Estática; caída narrativa de carga solo si definida.
- **Colisión e interacción:** Marcos/cargas principales sólidos; preservar rutas.
- **Firma sonora:** Crujido aislado contextual, no cada segundo.
- **Montaje y relaciones:** Anclajes y carga coherente, separar vista y cobertura física.
- **Prueba específica de acabado:** No rayos a través de caja sólida; no moiré de barras desde cámara.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-029 · Carro de carga

**Función:** Rigidbody empujable.

**Construcción exigida:** Chasis, ruedas, asa y plataforma.

- **Medidas objetivo:** 1 × 0.6 × 0.9 m.
- **Materiales y respuesta visual:** Chasis, pintura, metal y ruedas de goma.
- **Desgaste con causa:** Asa pulida, borde rayado y neumáticos usados.
- **Movimiento y estados:** Rigidbody con fuerza limitada, ruedas visuales simples.
- **Colisión e interacción:** Collider de cuerpo, centro de masa bajo, capa DynamicProp.
- **Firma sonora:** Contacto por fuerza, cooldown de ruido.
- **Montaje y relaciones:** Carga útil estable y dos carriles con fricción distinta.
- **Prueba específica de acabado:** Empujar, chocar, guardar y cargar sin velocidad residual.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-030 · Contenedor técnico

**Función:** Cobertura, no caja de color.

**Construcción exigida:** Paneles, esquinas, fijación y etiqueta.

- **Medidas objetivo:** 1.2 × 0.8 × 0.9 m.
- **Materiales y respuesta visual:** Paneles de chapa, esquinas y goma.
- **Desgaste con causa:** Golpes de transporte y cierres usados.
- **Movimiento y estados:** Estático o una variante dinámica explícita.
- **Colisión e interacción:** Collider de masa principal, cobertura real.
- **Firma sonora:** Metal al impacto, ruido según dinámica.
- **Montaje y relaciones:** Etiquetas seriales y carga compatible con taller.
- **Prueba específica de acabado:** Reconocer cierres, paneles y espesor; no cubo marrón final.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-031 · Motor/bomba

**Función:** Explica vibración de nave.

**Construcción exigida:** Carcasa, brida, eje protegido y tuberías.

- **Medidas objetivo:** 1.5 × 0.8 × 1 m.
- **Materiales y respuesta visual:** Metal, goma y conexiones de tubería.
- **Desgaste con causa:** Aceite cerca de unión, calor cerca de núcleo.
- **Movimiento y estados:** Vibración sutil y ventilación, no todo mesh temblando.
- **Colisión e interacción:** Bloque fijo.
- **Firma sonora:** Motor grave localizado y pulso mecánico.
- **Montaje y relaciones:** Base atornillada; bridas llevan a pipes existentes.
- **Prueba específica de acabado:** Tubos tienen destino; audio sale de máquina y se filtra por puertas.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-032 · Generador local

**Función:** Fuente activa de infraestructura.

**Construcción exigida:** Bloque, escape, radiador, base y conexiones.

- **Medidas objetivo:** 3 × 1.5 × 1.8 m.
- **Materiales y respuesta visual:** Metal, aislantes, radiador y montaje.
- **Desgaste con causa:** Mantenido en puntos funcionales, reparaciones de épocas distintas.
- **Movimiento y estados:** Loop leve; aspas/partes móviles protegidas.
- **Colisión e interacción:** Bloques de base, espacio de servicio libre.
- **Firma sonora:** Fuente grave, ventilación y rele ocasional.
- **Montaje y relaciones:** Alimentación y salida conectadas, no reactor decorativo.
- **Prueba específica de acabado:** Leer varias piezas funcionales sin miles de triángulos invisibles.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-033 · Cuadro de distribución

**Función:** Autorización A.

**Construcción exigida:** Módulos, indicadores, cableado y manijas.

- **Medidas objetivo:** 1.4 × 0.3 × 1.8 m.
- **Materiales y respuesta visual:** Chapa, indicadores, plástico y cable protegido.
- **Desgaste con causa:** Uso en manija, módulos recientes dentro.
- **Movimiento y estados:** Panel A cambia indicador y abre permiso.
- **Colisión e interacción:** Collider simple y control a distancia humana.
- **Firma sonora:** Contactor y liberación de compuerta real.
- **Montaje y relaciones:** Distribución eléctrica llega a equipos/luminaria.
- **Prueba específica de acabado:** Autorización modifica componentes y persiste en guardado.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-034 · Válvula grande

**Función:** Ruta técnica creíble.

**Construcción exigida:** Cuerpo, volante, bridas y tubo.

- **Medidas objetivo:** 0.45 m de volante; tubo 0.2–0.4 m.
- **Materiales y respuesta visual:** Metal pintado y bridas.
- **Desgaste con causa:** Agua y óxido en junta, contacto sobre volante.
- **Movimiento y estados:** Fija si decorativa; no inventar puzzle.
- **Colisión e interacción:** Collider de tubería principal, volante no engancha.
- **Firma sonora:** Ninguno salvo acción definida.
- **Montaje y relaciones:** Volante accesible, bridas alineadas con circuito.
- **Prueba específica de acabado:** No válvula flotante ni tubo terminado sin remate.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-035 · Extintor envejecido

**Función:** Referencia humana de escala.

**Construcción exigida:** Cilindro, manija, manguera y soporte.

- **Medidas objetivo:** 0.18 m diámetro × 0.55 m alto.
- **Materiales y respuesta visual:** Pintura, metal y manguera de goma.
- **Desgaste con causa:** Polvo localizado, etiqueta envejecida.
- **Movimiento y estados:** Estático.
- **Colisión e interacción:** Sin collider propio si sobre muro fuera de ruta.
- **Firma sonora:** Ninguno.
- **Montaje y relaciones:** Soporte y altura humana, no sobre piso sin causa.
- **Prueba específica de acabado:** Manija, boquilla y etiqueta distinguen del cilindro simple.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-036 · Soldador/carrito

**Función:** Reparación posterior EVA.

**Construcción exigida:** Equipo, ruedas, bobina y cables.

- **Medidas objetivo:** 0.9 × 0.5 × 0.8 m.
- **Materiales y respuesta visual:** Chapa, ruedas, cable y aislante.
- **Desgaste con causa:** Quemadura local, cable usado, carcasa reparada.
- **Movimiento y estados:** Estático; arco solo en ciclo de trabajo definido.
- **Colisión e interacción:** Bloque principal sin colisión por cable fino.
- **Firma sonora:** Loop de soldar solo cuando herramienta trabaja.
- **Montaje y relaciones:** Cable a brazo/herramienta y conexión de alimentación.
- **Prueba específica de acabado:** El arco tiene causa, no chispas emitidas desde nada.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-037 · Juego de herramientas

**Función:** Grupos sobre banco, atlas.

**Construcción exigida:** Llave, alicate, destornillador con agarres reales.

- **Medidas objetivo:** 0.12–0.3 m según herramienta.
- **Materiales y respuesta visual:** Metal expuesto y mangos dieléctricos.
- **Desgaste con causa:** Agarres pulidos y filos usados, medidas diferenciadas.
- **Movimiento y estados:** Estáticas agrupadas; no rig por herramienta.
- **Colisión e interacción:** Sin collider individual en set dressing.
- **Firma sonora:** Clink si cae una por evento, no ruido constante.
- **Montaje y relaciones:** Orden parcial de banco con función de cada herramienta.
- **Prueba específica de acabado:** Alicate, llave y destornillador reconocibles en silhouette.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-038 · Mesa de oficina

**Función:** Documentos y foto.

**Construcción exigida:** Tablero, cajones, patas y pasacables.

- **Medidas objetivo:** 1.6 × 0.75 × 0.75 m.
- **Materiales y respuesta visual:** Tablero, metal, plástico de borde.
- **Desgaste con causa:** Contactos de manos, círculo de taza, polvo protegido bajo papeles.
- **Movimiento y estados:** Cajón solo si documento lo usa.
- **Colisión e interacción:** Bloque principal con espacio frontal de silla.
- **Firma sonora:** Madera/metal de contacto y cajón opcional.
- **Montaje y relaciones:** Documentos/foto físicamente apoyados y cable con pasacables.
- **Prueba específica de acabado:** No texto flotante y no piernas atravesando drawer en pose.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-039 · Silla usada

**Función:** Historia de operarios.

**Construcción exigida:** Base, respaldo, asiento y ruedas.

- **Medidas objetivo:** 0.65 × 0.65 × 1 m.
- **Materiales y respuesta visual:** Metal, plástico y tela/goma elegida.
- **Desgaste con causa:** Asiento comprimido y apoyabrazos usados.
- **Movimiento y estados:** Estática; ruedas con apoyo real.
- **Colisión e interacción:** Collider simplificado no engancha rutas.
- **Firma sonora:** Chirrido solo si se mueve por escena.
- **Montaje y relaciones:** Ligeramente retirada del escritorio con causa humana.
- **Prueba específica de acabado:** Base completa y asiento de escala coherente.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-040 · Taza y termo

**Función:** Contraste de vida cotidiana.

**Construcción exigida:** Espesor, asa/tapa y desgaste.

- **Medidas objetivo:** Taza 0.09 m alto, termo 0.25 m.
- **Materiales y respuesta visual:** Cerámica o metal y tapa plástica.
- **Desgaste con causa:** Taza relativamente protegida, mancha localizada de uso.
- **Movimiento y estados:** Estáticos.
- **Colisión e interacción:** Sin collider propio en mesa.
- **Firma sonora:** Ninguno salvo recoger específico.
- **Montaje y relaciones:** Asa visible y apoyos sin penetración.
- **Prueba específica de acabado:** Pared interior con espesor y asa conectada, no cilindro sólido.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-041 · Jaula modular

**Función:** Humanos archivados, collider consistente.

**Construcción exigida:** Marco, barras, puerta, bisagras, cierre y piso.

- **Medidas objetivo:** 2.2 × 1.5 × 2.4 m módulo.
- **Materiales y respuesta visual:** Marco metálico, barras, cierre y piso.
- **Desgaste con causa:** Uso humano y mantenimiento reciente; sangre hacia drenaje.
- **Movimiento y estados:** Puerta estática o animada explícitamente; humano independiente.
- **Colisión e interacción:** Definir barras vs paneles sólidos; no cobertura falsa.
- **Firma sonora:** Metal y cierre; respiración pertenece al sujeto.
- **Montaje y relaciones:** Tubos por pasacables, placa fija y base apoyada.
- **Prueba específica de acabado:** Humanos caben; LOD no cambia injustamente cobertura.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-042 · Cierre de contención

**Función:** Explica sistema de jaulas.

**Construcción exigida:** Caja, pasador, actuador y luz de estado.

- **Medidas objetivo:** 0.3 × 0.15 × 0.2 m.
- **Materiales y respuesta visual:** Metal, actuador y luz de estado.
- **Desgaste con causa:** Uso en pasador, carcasa revisada recientemente.
- **Movimiento y estados:** Actuador se libera solo si historia lo autoriza.
- **Colisión e interacción:** Integrado a puerta, sin duplicar trigger.
- **Firma sonora:** Latch y servo acotados.
- **Montaje y relaciones:** Alineado al pasador y marco, cable a control.
- **Prueba específica de acabado:** Cerrar realmente sujeta; no cerrojo que flota lejos de puerta.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-043 · Camilla clínica

**Función:** Soporte humano.

**Construcción exigida:** Bastidor, colchón, ruedas, freno y baranda.

- **Medidas objetivo:** 2 × 0.75 × 0.8 m.
- **Materiales y respuesta visual:** Metal sanitario, colchón, goma y tela.
- **Desgaste con causa:** Uso y compresión donde cuerpo toca, ruedas gastadas.
- **Movimiento y estados:** Humano respira; camilla quieta salvo variante dinámica.
- **Colisión e interacción:** Collider cama separado del sujeto.
- **Firma sonora:** Freno/metal por evento; pump es fuente separada.
- **Montaje y relaciones:** Tubos y equipo con soporte, humano correctamente apoyado.
- **Prueba específica de acabado:** Ruedas, barandas y frenos reales; piel no atraviesa manta.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-044 · Mesa de procedimientos

**Función:** Escena focal clínica.

**Construcción exigida:** Base, juntas, apoyo y mecanismos.

- **Medidas objetivo:** 2.1 × 0.8 × 0.9 m.
- **Materiales y respuesta visual:** Metal, tapizado y juntas mecánicas.
- **Desgaste con causa:** Limpieza parcial y marcas de procedimiento.
- **Movimiento y estados:** Soporte ajusta solo en escena autorada.
- **Colisión e interacción:** Base/cuerpo, joints visuales no dañan por callback extra.
- **Firma sonora:** Motor corto y click de soporte.
- **Montaje y relaciones:** Lámpara/equipo llega a sujeto con alcance plausible.
- **Prueba específica de acabado:** No mesa plana gris ni restricción que atraviesa cuerpo.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-045 · Monitor biométrico

**Función:** Mantenimiento de sujetos.

**Construcción exigida:** Pantalla, soporte, conectores y botones.

- **Medidas objetivo:** 0.45 × 0.15 × 0.35 m.
- **Materiales y respuesta visual:** Housing de polímero, pantalla y mount metálico.
- **Desgaste con causa:** Botones usados, pantalla mantenida.
- **Movimiento y estados:** Dato relevante actualiza lentamente.
- **Colisión e interacción:** Sin collider extra sobre soporte salvo interacción.
- **Firma sonora:** Beep bajo opcional, no en toda sala.
- **Montaje y relaciones:** Cable a equipo/paciente ficticio, soporte estable.
- **Prueba específica de acabado:** Monitor legible y no número random frenético.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-046 · Bomba de perfusión ficticia

**Función:** Animación mínima / sonido bajo.

**Construcción exigida:** Housing, tubos, montaje y datos.

- **Medidas objetivo:** 0.2 × 0.15 × 0.25 m.
- **Materiales y respuesta visual:** Plástico, metal y tubos de goma.
- **Desgaste con causa:** Equipo reciente con etiqueta de unidad.
- **Movimiento y estados:** Ciclo lento, flujo sugerido sin simulación médica.
- **Colisión e interacción:** Integrada al stand, no obstáculo pequeño aislado.
- **Firma sonora:** Click lento localizado.
- **Montaje y relaciones:** Tubos con punto de conexión claro y slack para respiración.
- **Prueba específica de acabado:** No tubos flotantes ni atraviesan mano durante loop.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-047 · Soporte de fluidos

**Función:** Tubos con destino.

**Construcción exigida:** Base estable, eje y ganchos.

- **Medidas objetivo:** 0.6 m base × 1.7 m alto.
- **Materiales y respuesta visual:** Metal, ruedas/goma y bolsas ficticias.
- **Desgaste con causa:** Apoyos usados, frame limpio funcional.
- **Movimiento y estados:** Estático.
- **Colisión e interacción:** Base simplificada si en camino; no enganche por patas finas.
- **Firma sonora:** Ninguno fuera de contacto.
- **Montaje y relaciones:** Centro estable, fluidos y bomba sujetos.
- **Prueba específica de acabado:** Altura humana y tubos no se estiran imposible.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-048 · Lámpara clínica

**Función:** Luz focal, no todas dinámicas.

**Construcción exigida:** Cabezal, lentes, joints y brazo.

- **Medidas objetivo:** 0.6 m cabezal; brazo 1–1.5 m.
- **Materiales y respuesta visual:** Metal, polímero, lentes y joint.
- **Desgaste con causa:** Grips usados, vidrio/lente distinto del marco.
- **Movimiento y estados:** Brazo quieto o clip lento probado.
- **Colisión e interacción:** Mount estático fuera de circulación.
- **Firma sonora:** Joint solo al moverse.
- **Montaje y relaciones:** Anclaje soporta peso y cono cae sobre procedimiento.
- **Prueba específica de acabado:** Luz sale de cabezal; no spot invisible separado un metro.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-049 · Bandeja instrumental

**Función:** Horror sugerido y función.

**Construcción exigida:** Bandeja con espesor, pinzas/herramientas.

- **Medidas objetivo:** 0.5 × 0.35 × 0.06 m.
- **Materiales y respuesta visual:** Acero y herramientas ficticias.
- **Desgaste con causa:** Uso localizado, sangre mínima con causa.
- **Movimiento y estados:** Estática.
- **Colisión e interacción:** Sin collider por pinza individual.
- **Firma sonora:** Clink contextual.
- **Montaje y relaciones:** Bandeja en carro/mesa, no levitando cerca de paciente.
- **Prueba específica de acabado:** Espesor y escala de instrumentos, no prismas idénticos.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-050 · Brazo clínico

**Función:** Movimiento ambiental aislado.

**Construcción exigida:** Joints, herramienta ficticia, cableado.

- **Medidas objetivo:** Radio de trabajo 1.2–1.8 m.
- **Materiales y respuesta visual:** Metal sanitario, actuadores y cables.
- **Desgaste con causa:** Mantenido y marcas cerca de herramienta.
- **Movimiento y estados:** Un ciclo autorado con pausa larga; herramienta ficticia.
- **Colisión e interacción:** Base principal, no daño ambiental implícito.
- **Firma sonora:** Servo bajo distinto del Vigía.
- **Montaje y relaciones:** Montaje al equipo y recorrido sin contacto imposible.
- **Prueba específica de acabado:** No atraviesa sujeto ni tubo; no parece ataque con mismo telegraph de bot.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-051 · Lavamanos industrial

**Función:** Causa de humedad.

**Construcción exigida:** Cubeta, grifo, soporte y drenaje.

- **Medidas objetivo:** 0.8 × 0.6 × 0.9 m.
- **Materiales y respuesta visual:** Cerámica/metal y tubería.
- **Desgaste con causa:** Cal y humedad desde grifo/drenaje.
- **Movimiento y estados:** Goteo limitado si source activo.
- **Colisión e interacción:** Bloque estático.
- **Firma sonora:** Gota real en punto coherente.
- **Montaje y relaciones:** Grifo, desagüe, sifón y conexión, soporte visible.
- **Prueba específica de acabado:** Se entiende dónde va el agua y la mancha corresponde.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-052 · Rejilla de drenaje

**Función:** Conecta sangre/agua.

**Construcción exigida:** Marco y láminas con espesor cercano.

- **Medidas objetivo:** 0.6 × 0.2 m, o panel 1 × 1 m.
- **Materiales y respuesta visual:** Metal con marco.
- **Desgaste con causa:** Agua/sangre hacia punto bajo, desgaste en borde.
- **Movimiento y estados:** Estática.
- **Colisión e interacción:** Superficie caminable sin hueco que engancha cápsula.
- **Firma sonora:** Paso metálico húmedo según zona.
- **Montaje y relaciones:** Pendiente visual y canal conectados.
- **Prueba específica de acabado:** Láminas tienen espesor cercano, sin moiré dominante.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-053 · Biombo

**Función:** Revelación por silueta.

**Construcción exigida:** Marco, patas, ruedas y panel/tela.

- **Medidas objetivo:** 1.5 × 0.5 × 1.8 m.
- **Materiales y respuesta visual:** Metal y tela/panel elegido.
- **Desgaste con causa:** Borde/tela usados, ruedas apoyadas.
- **Movimiento y estados:** Estático o apartarse por acción guionada.
- **Colisión e interacción:** Bloque coherente con visibilidad y uso de cobertura.
- **Firma sonora:** Tela/rueda si acción lo exige.
- **Montaje y relaciones:** Soportes permiten mantenerlo vertical.
- **Prueba específica de acabado:** No plano flotante que funciona como muro invisible sólido.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-054 · Vendajes y manta

**Función:** Cuerpos parcialmente cubiertos.

**Construcción exigida:** Volumen/pliegues de tela, zonas de presión.

- **Medidas objetivo:** Manta 1.6 × 1 m; vendas escala anatómica.
- **Materiales y respuesta visual:** Tela y fibras en normal moderado.
- **Desgaste con causa:** Presión, humedad y desgaste local.
- **Movimiento y estados:** Sigue respiración leve si skinned, sin cloth caro necesario.
- **Colisión e interacción:** Sin collider propio que atrape humano/player.
- **Firma sonora:** Roce integrado al sujeto.
- **Montaje y relaciones:** Caída y pliegues por soporte/peso del cuerpo.
- **Prueba específica de acabado:** Tela con grosor/borde, no tapa rígida sobre torso que se mueve.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-055 · Prótesis experimental

**Función:** Distorsión narrativa específica.

**Construcción exigida:** Fijaciones y transición al cuerpo.

- **Medidas objetivo:** 0.25–0.7 m según sujeto.
- **Materiales y respuesta visual:** Metal, polímero y transición a piel.
- **Desgaste con causa:** Uso reciente en apoyo, cicatriz localizada.
- **Movimiento y estados:** Articula según rig humano si se mueve.
- **Colisión e interacción:** Collider solo si cambia bloque del conjunto.
- **Firma sonora:** Joint tenue si se acciona.
- **Montaje y relaciones:** Fijación específica y anatomía coherente del injerto.
- **Prueba específica de acabado:** No pieza mecánica pegada sin transición ni peso.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-056 · Jeringa ficticia

**Función:** Curación con animación.

**Construcción exigida:** Cuerpo, émbolo, tapa y líquido.

- **Medidas objetivo:** 0.15 m largo.
- **Materiales y respuesta visual:** Cuerpo transparente controlado, plástico y líquido ficticio.
- **Desgaste con causa:** Envase actual, no instrumento oxidado abandonado.
- **Movimiento y estados:** Émbolo y gesto de uso coinciden con consumo.
- **Colisión e interacción:** Pickup y viewmodel separados.
- **Firma sonora:** Tapa/roce y exhalación leves.
- **Montaje y relaciones:** En stock clínico o gabinete, no siempre sobre suelo.
- **Prueba específica de acabado:** Mano agarre correcto; cura al finalizar sin atravesar brazo.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-057 · Ración sellada

**Función:** Curación, lote EVA.

**Construcción exigida:** Envoltura, costura y etiqueta reciente.

- **Medidas objetivo:** 0.2 × 0.12 × 0.04 m.
- **Materiales y respuesta visual:** Envase flexible, impresión y sello.
- **Desgaste con causa:** Pliegues de transporte, lote actual.
- **Movimiento y estados:** Abrir/usar clip compacto sin gameplay adicional.
- **Colisión e interacción:** Pickup parcial no aplica: unidad discreta.
- **Firma sonora:** Envoltura breve.
- **Montaje y relaciones:** Caja/repisas de mantenimiento reciente.
- **Prueba específica de acabado:** Fecha explica alimento conservado; no ladrillo amarillo de color.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-058 · Atril de admisión

**Función:** Clasificación corporativa.

**Construcción exigida:** Pedestal, soporte, carpeta y cierre.

- **Medidas objetivo:** 0.6 × 0.5 × 1.2 m.
- **Materiales y respuesta visual:** Metal/polímero, carpeta y control.
- **Desgaste con causa:** Zona de manos usada, registro añadido de EVA.
- **Movimiento y estados:** Pantalla o ficha responde a interacción.
- **Colisión e interacción:** Housing y Interactable simple.
- **Firma sonora:** Click bajo, lectura pausa.
- **Montaje y relaciones:** Altura de recepción y zona de fila.
- **Prueba específica de acabado:** Carpeta montada y texto legible sin plano flotante.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-059 · Terminal de expediente

**Función:** Archivo opcional.

**Construcción exigida:** Pantalla, teclado/control y base.

- **Medidas objetivo:** 0.6 × 0.45 × 1.2 m.
- **Materiales y respuesta visual:** Carcasa, pantalla, vidrio discreto y control.
- **Desgaste con causa:** Teclas usadas, carcasa mantenida.
- **Movimiento y estados:** Documento seleccionado, sin animación random.
- **Colisión e interacción:** Collider de cuerpo y punto de interacción claro.
- **Firma sonora:** UI sobria, ventilación cercana.
- **Montaje y relaciones:** Cable a rack y apoyo/stand reales.
- **Prueba específica de acabado:** Leer texto bajo luz neutra y sector sin reflejo que lo oculte.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-060 · Vidrio de observación

**Función:** Transparencia/reflejo controlado.

**Construcción exigida:** Marco, grosor y sellos.

- **Medidas objetivo:** Paño 3–6 × 2–3 m.
- **Materiales y respuesta visual:** Vidrio, metal y sellos.
- **Desgaste con causa:** Condensación localizada y contacto humano.
- **Movimiento y estados:** Estático; huellas de escena por decal.
- **Colisión e interacción:** Muro de vidrio real bloquea ataque si es irrompible.
- **Firma sonora:** Atenuación de sala tras vidrio, golpe solo autorado.
- **Montaje y relaciones:** Marco con espesor y sala real del otro lado.
- **Prueba específica de acabado:** Transparency sin sorting grave y vista coherente a sujetos.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-061 · Cámara de vigilancia

**Función:** Algunas dañadas, explica puntos ciegos.

**Construcción exigida:** Soporte, housing, lente y cable.

- **Medidas objetivo:** 0.3 × 0.2 × 0.2 m.
- **Materiales y respuesta visual:** Housing, lente, soporte y cable.
- **Desgaste con causa:** Algunas rotas y otras mantenidas.
- **Movimiento y estados:** Giro lento solo en cámaras activas definidas.
- **Colisión e interacción:** Sin collider fino separado en techo.
- **Firma sonora:** Servo solo al girar, no enemigo falso continuo.
- **Montaje y relaciones:** Mount y cable, ángulo coincide con punto ciego.
- **Prueba específica de acabado:** No cámara mira a sótano antes de detección; lore y percepción consistentes.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-062 · Placa de sujeto

**Función:** Historia de personas.

**Construcción exigida:** Numeración, soporte y registro.

- **Medidas objetivo:** 0.2 × 0.1 m.
- **Materiales y respuesta visual:** Metal/plástico y impresión.
- **Desgaste con causa:** Nombre anterior parcialmente cubierto por serial.
- **Movimiento y estados:** Estática.
- **Colisión e interacción:** Sin collider dedicado.
- **Firma sonora:** Ninguno.
- **Montaje y relaciones:** En módulo de jaula, no flota frente al humano.
- **Prueba específica de acabado:** Nombre/número legibles cerca y compatibles con expediente.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-063 · Pizarra de turnos

**Función:** Contraste entre humanos y régimen.

**Construcción exigida:** Marco, anotaciones y marcas viejas.

- **Medidas objetivo:** 1.2 × 0.8 m.
- **Materiales y respuesta visual:** Marco, tablero y anotaciones originales.
- **Desgaste con causa:** Borrado parcial, polvo protegido bajo ficha.
- **Movimiento y estados:** Estática.
- **Colisión e interacción:** Parte de muro.
- **Firma sonora:** Ninguno.
- **Montaje y relaciones:** Oficina clínica, turnos anteriores al régimen.
- **Prueba específica de acabado:** Texto tiene significado y no decorado ilegible repetido.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-064 · Bolsas/contenedor clínico

**Función:** Set dressing localizado.

**Construcción exigida:** Cierre, volumen y señalización.

- **Medidas objetivo:** 0.4 × 0.3 × 0.6 m.
- **Materiales y respuesta visual:** Polímero, bolsa opaca y tapa.
- **Desgaste con causa:** Uso reciente localizado, señalización sanitaria.
- **Movimiento y estados:** Estático.
- **Colisión e interacción:** Bloque simple si en suelo, no accesorio que engancha.
- **Firma sonora:** Ninguno fuera de acción.
- **Montaje y relaciones:** Junto a procedimiento/drenaje, no por todo pasillo.
- **Prueba específica de acabado:** Volumen y cierre, bolsa no parece cubo pintado.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-065 · Altavoz de megafonía

**Función:** Anuncio reverberante exterior.

**Construcción exigida:** Rejilla, carcasa, soporte y cable.

- **Medidas objetivo:** 0.4 × 0.3 × 0.25 m.
- **Materiales y respuesta visual:** Metal/plástico y rejilla.
- **Desgaste con causa:** Carcasa antigua, cable recientemente reparado.
- **Movimiento y estados:** Estático, emisión de anuncio una vez.
- **Colisión e interacción:** Collider de mount si necesario, no trigger de detección en speaker.
- **Firma sonora:** Voz filtrada, alerta y reverb real del corredor.
- **Montaje y relaciones:** Fuera de sótano, altura plausible con soporte y cable.
- **Prueba específica de acabado:** Escuchar ubicación exterior con puerta cerrada/abierta y subtítulos.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-066 · Luminaria técnica

**Función:** Fuentes plausibles de luz.

**Construcción exigida:** Housing, difusor, anclajes y cable.

- **Medidas objetivo:** 0.8 × 0.2 × 0.15 m.
- **Materiales y respuesta visual:** Metal, difusor y cable.
- **Desgaste con causa:** Polvo arriba y difusión irregular, no grunge sobre todo.
- **Movimiento y estados:** Flicker solo autorado y desactivable.
- **Colisión e interacción:** Sin collider fuera del paso.
- **Firma sonora:** Hum bajo puntual, nunca en todas las fuentes.
- **Montaje y relaciones:** Anclajes al techo, luz nace de housing.
- **Prueba específica de acabado:** Sombra y emisión coherentes, no plafón sin instalación.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-067 · Lámpara de emergencia

**Función:** Orientación ámbar.

**Construcción exigida:** Carcasa, lente, soporte y etiqueta.

- **Medidas objetivo:** 0.3 × 0.15 × 0.12 m.
- **Materiales y respuesta visual:** Carcasa, lente ámbar y bracket.
- **Desgaste con causa:** Etiqueta antigua y mantenida.
- **Movimiento y estados:** Estable o pulso lento sin strobe.
- **Colisión e interacción:** Parte de muro.
- **Firma sonora:** Sin loop extra salvo alarma vinculada.
- **Montaje y relaciones:** En acceso/refugio con función de orientación.
- **Prueba específica de acabado:** No confundirse con carga de red/rayo; color no es única guía.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-068 · Bandeja de cables

**Función:** Escala y función de galerías.

**Construcción exigida:** Perfiles, ménsulas y haces ordenados.

- **Medidas objetivo:** Módulos 2/4 m largo × 0.3–0.6 m ancho.
- **Materiales y respuesta visual:** Metal, cable aislado y fijaciones.
- **Desgaste con causa:** Polvo/agua según ubicación, cinchas recientes.
- **Movimiento y estados:** Estático, cables no serpentean sin causa.
- **Colisión e interacción:** No collider por cable alto.
- **Firma sonora:** Ninguno salvo resonancia ambiental ligada.
- **Montaje y relaciones:** Ménsulas y rutas hacia cuadro/rack, terminaciones reales.
- **Prueba específica de acabado:** Seguir haces sin cables que desaparecen a mitad de techo.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-069 · Conducto/rejilla ventilación

**Función:** Fuente localizada de aire.

**Construcción exigida:** Juntas, paneles y fijaciones.

- **Medidas objetivo:** Módulos 2/4 m, sección 0.5–1 m.
- **Materiales y respuesta visual:** Chapa, rejilla y joints.
- **Desgaste con causa:** Humedad por salida, polvo según flujo.
- **Movimiento y estados:** Ventilación sugerida por partículas leves.
- **Colisión e interacción:** Collider principal si obstáculo, no pieza por lámina.
- **Firma sonora:** Aire localizado y ocluido.
- **Montaje y relaciones:** Bridas, soportes, entrada/salida conectada.
- **Prueba específica de acabado:** Ancho/soporte plausible y no conducto cortado sin remate.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-070 · Puerta corrediza pesada

**Función:** Apertura real con obstrucción.

**Construcción exigida:** Hojas, rieles, motores, sellos y sensores.

- **Medidas objetivo:** Paso 3 × 3.5 m, marco externo mayor.
- **Materiales y respuesta visual:** Chapa, riel, goma, sensor y motor.
- **Desgaste con causa:** Contacto de hoja y guía, pintura usada.
- **Movimiento y estados:** Abrir 1.5–2.5 s con aceleración/freno; obstrucción comprobada.
- **Colisión e interacción:** Collider acompaña hoja; snapshot de estado consistente.
- **Firma sonora:** Motor, guía y fin sonoro.
- **Montaje y relaciones:** Cavidad lateral/hojas tiene espacio físico donde desplazarse.
- **Prueba específica de acabado:** No desaparece mesh para abrir ni aplasta jugador sin regla.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-071 · Esclusa de presión

**Función:** Transición y refugio.

**Construcción exigida:** Marcos, actuadores, juntas y controles.

- **Medidas objetivo:** Paso 3 × 3.5 m, cámara entre dos hojas.
- **Materiales y respuesta visual:** Metal, juntas, actuadores y controles.
- **Desgaste con causa:** Mantenida en refugio, marcas antiguas de uso.
- **Movimiento y estados:** Secuencia de puertas segura, nunca ambas dañando simultáneamente.
- **Colisión e interacción:** Estado sincronizado con permisos y navegación.
- **Firma sonora:** Presión, motor y fin; aislamiento auditivo perceptible.
- **Montaje y relaciones:** Volumen entre puertas permite estar sin quedar fuera de mapa.
- **Prueba específica de acabado:** Entrada da respiro real, enemigo no dispara a través de hoja cerrada.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-072 · Rack de control

**Función:** Infraestructura activa EVA.

**Construcción exigida:** Bastidor, módulos, ventiladores y cables.

- **Medidas objetivo:** 0.8 × 0.8 × 2.2 m por rack.
- **Materiales y respuesta visual:** Metal, módulos, ventilación y cables.
- **Desgaste con causa:** Piezas recientes contrastan con bastidor viejo.
- **Movimiento y estados:** Fans limitados, LEDs moderados con datos relevantes.
- **Colisión e interacción:** Bloque estático, espacio de mantenimiento libre.
- **Firma sonora:** Ventilación grave/baja, no cada LED emite audio.
- **Montaje y relaciones:** Entrada/salida de cableado y enfriamiento.
- **Prueba específica de acabado:** Módulos tienen panel, espesor y serial, no pared de prismas coloridos.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-073 · Consola principal

**Función:** Revelación y permiso final.

**Construcción exigida:** Paneles, pantallas, teclas y mantenimiento.

- **Medidas objetivo:** 2.4 × 0.9 × 1.2 m.
- **Materiales y respuesta visual:** Carcasa, control, pantallas y bisagras.
- **Desgaste con causa:** Grips/tablero usados, pantallas actuales.
- **Movimiento y estados:** Interacción final/archivo con UI original.
- **Colisión e interacción:** Collider de mesa y distancia humana.
- **Firma sonora:** Click, relé y mensaje opcional sobrio.
- **Montaje y relaciones:** Orientada a arena/infraestructura, cableado con destino.
- **Prueba específica de acabado:** Leer responsabilidad de empresa y abrir permiso correcto.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-074 · Monitor mural

**Función:** Jaulas y estado humano.

**Construcción exigida:** Marco, anclaje y datos originales.

- **Medidas objetivo:** 1.2 × 0.7 × 0.1 m.
- **Materiales y respuesta visual:** Marco, display y soporte.
- **Desgaste con causa:** Polvo en borde, mantenimiento de panel.
- **Movimiento y estados:** Estados de jaulas/detección sin loops contradictorios.
- **Colisión e interacción:** Parte de muro, no trigger independiente.
- **Firma sonora:** Ninguno salvo fuente narrativa real.
- **Montaje y relaciones:** Soporte y cable, datos vinculados a sectores.
- **Prueba específica de acabado:** No video de sujeto en estado distinto del mundo guardado.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-075 · Baranda/pasarela

**Función:** Profundidad/escala de nave.

**Construcción exigida:** Perfiles, uniones, apoyos y piso.

- **Medidas objetivo:** Ancho 2.5–3 m, tramo según nave.
- **Materiales y respuesta visual:** Acero, rejilla/piso y baranda.
- **Desgaste con causa:** Pasos usados, humedad donde corresponde.
- **Movimiento y estados:** Estática.
- **Colisión e interacción:** Suelo continuo y baranda simple; agente solo si ruta validada.
- **Firma sonora:** Paso metálico con acústica de nave.
- **Montaje y relaciones:** Apoyos/bases estructurales y acceso real.
- **Prueba específica de acabado:** No pasarela sin columnas ni baranda a altura inhumana.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-076 · Columna con servicios

**Función:** Cobertura y composición.

**Construcción exigida:** Estructura, cubierta, registros y base.

- **Medidas objetivo:** 0.8–1.2 m sección, 4–9 m alto.
- **Materiales y respuesta visual:** Concreto/metal y paneles de servicios.
- **Desgaste con causa:** Base húmeda, registros usados.
- **Movimiento y estados:** Estática.
- **Colisión e interacción:** Cobertura sólida, no ocultar collider por tamaño visual menor.
- **Firma sonora:** Impacto según superficie.
- **Montaje y relaciones:** Base y vigas, líneas de servicio con registro.
- **Prueba específica de acabado:** Jefe/proyectiles bloqueados y jugador puede rodear sin atasco.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-077 · Panel exterior de escape

**Función:** Interacción final.

**Construcción exigida:** Botón/manija, luz y placa.

- **Medidas objetivo:** 0.35 × 0.15 × 0.5 m.
- **Materiales y respuesta visual:** Carcasa, control y indicador.
- **Desgaste con causa:** Uso de emergencia antiguo y piezas mantenidas.
- **Movimiento y estados:** Botón/manija libera salida tras permiso.
- **Colisión e interacción:** Interactable independiente del trigger de victoria.
- **Firma sonora:** Actuador, relé y aire exterior.
- **Montaje y relaciones:** Junto a compuerta, altura humana.
- **Prueba específica de acabado:** No gana al tocar panel; gana cruzando exterior seguro.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-078 · Compuerta monumental

**Función:** Salida del búnker.

**Construcción exigida:** Hojas, cerradura, pistones y junta.

- **Medidas objetivo:** Paso 5–6 m ancho × 5–6 m alto.
- **Materiales y respuesta visual:** Hojas metálicas, pistones, joints y cierres.
- **Desgaste con causa:** Daño/uso monumental localizado, sellos mantenidos.
- **Movimiento y estados:** Apertura progresiva con masa aparente y fin definido.
- **Colisión e interacción:** Collider de hojas, paso exterior seguro.
- **Firma sonora:** Pistones, presión, mecanismo y nuevo ambiente.
- **Montaje y relaciones:** Espacio para mover hojas, bases y guías visibles.
- **Prueba específica de acabado:** No revela backstage ni usa blanco total para esconder exterior.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-079 · Ventilador industrial

**Función:** Silueta móvil con costo medido.

**Construcción exigida:** Housing, aspas y guardas.

- **Medidas objetivo:** 1–2 m diámetro en housing.
- **Materiales y respuesta visual:** Metal, aspas, guardas y motor.
- **Desgaste con causa:** Polvo y mantenimiento según uso.
- **Movimiento y estados:** Rotación con límites/LOD, evitar aliasing de aspas.
- **Colisión e interacción:** Housing fijo; no daño por guarda salvo diseño explícito.
- **Firma sonora:** Aire y motor con punto de fuente.
- **Montaje y relaciones:** Anclajes y ducto real; luz puede recortar silueta.
- **Prueba específica de acabado:** Movimiento plausible sin ruido visual ni costo de sombra excesivo.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

### OBJ-080 · Archivo físico/fotos

**Función:** Pistas y easter eggs por sala.

**Construcción exigida:** Hojas con espesor agrupado, carpetas y soporte.

- **Medidas objetivo:** Hoja A4 aproximada, carpetas/fotos variadas.
- **Materiales y respuesta visual:** Papel, cartón, vidrio/marco y tinta.
- **Desgaste con causa:** Bordes, presión, polvo y protección por objetos encima.
- **Movimiento y estados:** Estáticos; documento abierto mediante UI accesible.
- **Colisión e interacción:** Sin collider por hoja; interacción agrupada por documento.
- **Firma sonora:** Papel breve al abrir, lectura pausa.
- **Montaje y relaciones:** Apoyos reales, DOC-01 a DOC-12 según sala.
- **Prueba específica de acabado:** Doce textos distintos, legibilidad y autoría, nada de lorem ipsum final.

**Registro de producción:** asignar Tier, fuente/export/prefab, tris y sets reales, pendientes y evidencia ART aplicable. No dar por terminado por tener material de color.

## Revisión de conjunto

Revisar primero los contactos entre objetos: cámara-mano, arma-grip, jaula-sujeto, camilla-manta, puerta-riel, tubería-máquina, lámpara-cono y carro-suelo. Después comprobar pasillos libres, cobertura real, escala compartida, repetición y mezcla sonora. Un objeto correcto aislado puede fallar en su sala.

No colocar todas las familias en todos los cuartos. Usar las fichas SCN-01 a SCN-22 del maestro para selección y puesta en escena. Conservar población, munición y checkpoint del diseño; un prop adicional no implica nueva recompensa o enemigo.

Aceptar el objeto solo con evidencia de la prueba específica y los criterios ART aplicables. Si falla, registrar problema concreto y siguiente corrección; no esconderlo con oscuridad o desenfoque.
