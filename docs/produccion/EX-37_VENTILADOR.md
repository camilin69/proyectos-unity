# EX-37 · Ventilador industrial OBJ-079

Fuente original de 3624 triángulos, dentro del presupuesto 4000. Envolvente Blender XYZ 1.60 × 0.663 × 1.65 m, con flange de 1.60 m de diámetro y pies a suelo. Dos meshes —Housing y Rotor— comparten un atlas PBR 1024 de cuatro mapas. La carcasa es hueca; tiene bridas atornilladas, guardas delantera y trasera, seis aspas inclinadas con espesor, cubo/eje, motor posterior, tres apoyos radiales, caja de conexiones, cable y cuatro anclajes de suelo. La guarda trasera deja paso al eje.

## Presentación y colisión

IndustrialFanReview crea un pivote de rotor en Unity `(0,0.85,0)`, con rotación sobre Z local. Las aspas no arrastran el housing. IndustrialFan usa 12 RPM por defecto y limita el valor efectivo a 15 RPM. Solo actualiza con cámara principal, renderer visible y distancia máxima de 25 m; usa deltaTime, por lo que pausa detiene el giro. Esto limita actualizaciones, pero no constituye una medición de rendimiento ni un LOD geométrico.

El rotor no proyecta sombras dinámicas para evitar el coste de sombras de seis aspas. Doce cajas segmentan el perímetro fijo y siete cajas delgadas coinciden con las barras verticales de la guarda frontal. No hay collider en el rotor ni componente de daño. No se añadió AudioSource silencioso como sustituto de producir el audio requerido.

## Evidencia

Script reproducible `SourceArt/Scripts/build_fan_ex37.py`, fuente Blender empaquetada, FBX, prefab y evidencia en `SourceArt/_evidence/EX-37/OBJ-079_VentiladorIndustrial`. Capturas frontal, posterior y cuatro fases del rotor a 0/15/30/45 grados revisadas. Son vistas estáticas de holgura y silueta, no una prueba de ausencia de aliasing temporal.

Suite completa **107/107 Edit Mode**, trabajo `59ce6a6d3f8a476c98fccbe2f68c5b5a`, 3.4848392 s. Dos pruebas nuevas comprueban pivote, presupuesto, mapas, ausencia de colisión móvil, sombras del rotor, avance angular y límite de velocidad. XML nativo en EX-37.

Prueba **1/1 Play Mode específica**, trabajo `93e8c040d92347b49dbe65e9c8c118ba`, 0.4426808 s: Update gira con cámara cercana, pausa congela y distancia de 40 m detiene el avance. La primera ejecución falló por un error de backbuffer de URP; la cámara del test se cambió a RenderTexture fija, sin ignorar logs. XML nativo en EX-37. No se ejecutó una nueva suite Play Mode completa ni build; el prefab no está colocado todavía en campaña.

La medición de vértices fuente da radio máximo de rotor 0.625 m frente a interior de ducto 0.70 m; su extremo delantero queda en -0.1005 m y la guarda en -0.192 m.

## Pendientes

Prefab preparado; todavía no instalado en una región. Faltan ducto/anclaje de escena, audio localizado de aire/motor, LOD de geometría, perfil de rendimiento y revisión de aliasing durante el recorrido. El polvo y desgaste deben afinarse según su ubicación final. No se declara Conforme ni se cierra el objetivo global.
