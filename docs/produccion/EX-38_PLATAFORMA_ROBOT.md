# EX-38 · Plataforma de mantenimiento OBJ-021

Fuente Blender original de 2916 triángulos, dentro del presupuesto 3000, un mesh y atlas PBR 1024. Envolvente real Blender XYZ 2.60 × 1.3985 × 0.350 m, equivalente a la ficha de 2.6 × 1.4 × 0.35 m. Incluye dos raíles longitudinales, bastidor transversal, tres paneles desmontables, pies y anclajes, cuatro apoyos de goma, cuatro mordazas con carro/tornillo/pomo, dos tomas de servicio y cable aparcado sobre la cubierta.

El lateral de servicio queda retranqueado para alojar los conectores dentro de la anchura objetivo sin enterrarlos en la chapa. Las zonas de contacto usan goma; el acabado y desgaste específico de servicio todavía necesitan revisión artística. La base tiene una colisión sólida simplificada de 2.6 × 1.4 × 0.28 m.

## Prefabs y escala del robot

`OBJ-021_PlataformaRobot.prefab` contiene la base. `RobotMaintenance_EX38.prefab` añade una instancia visual del FBX existente BOT-02_Custodio, acostado sin cambiar la escala. No se instancia el prefab enemigo: el conjunto no recibe IA, Health, AudioSource, Animator ni collider del robot. Reutiliza el material del Custodio; no duplica su fuente de modelado.

El robot cabe en 2.6 m de longitud y 1 m de ancho entre las mordazas. La cota inferior global del robot queda a 0.280 m. Esto demuestra encaje de envolvente, pero no contacto correcto de cada pieza con cada apoyo: es un conjunto preparado para ajustar, no una pose de reparación aceptada. Los cables siguen aparcados y no se afirma que estén acoplados al cuerpo.

## Evidencia

`SourceArt/Scripts/build_robot_platform_ex38.py`, fuente `.blend`, FBX, cuatro mapas PBR, reporte de geometría, comprobación de ejes y capturas de plataforma/conjunto en `SourceArt/_evidence/EX-38/OBJ-021_PlataformaRobot`. Importación con error de coordenadas cero.

Suite **109/109 Edit Mode**, trabajo `4ad1fb8586aa4833b654e115c9e7456a`, 3.4315286 s; XML nativo en EX-38. Comprueba escala, textura y colisión de la plataforma, encaje del robot original, centrado, presupuesto y ausencia de componentes de combate. No se ejecutó nueva suite Play Mode ni build: no hay comportamiento nuevo ni colocación regional.

## Pendientes

M024 reserva 2 × 2 m y el objeto mide 2.6 m de largo. Resolver la composición y rutas con su brazo de reparación antes de montarlo; no se estira ni comprime el robot para ocultar esa diferencia. Faltan contacto individual de apoyos, cierre/posición de mordazas, conexión real de cables, brazo OBJ-020 y contacto sonoro durante reparación. Estado Prefab validado, aceptación no probada. El objetivo global sigue activo.
