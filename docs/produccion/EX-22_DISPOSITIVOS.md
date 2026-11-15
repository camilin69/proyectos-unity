# EX-22 · Monitor y bomba de perfusión

OBJ-045 MonitorBiometrico: 1840 triángulos, 0.44 × 0.35 × 0.154 m en Unity. OBJ-046 BombaPerfusion: 1820 triángulos, 0.20 × 0.25 × 0.207 m, incluyendo abrazadera. Ambos cuentan con fuente Blender, FBX, atlas PBR 1024 y prefab; una malla y un material geométrico, más texto dinámico de pantalla. No añaden colisiones pequeñas al carro o soporte que los sostiene.

El monitor sustituye M044 en REG-S3 sobre un carro sanitario, apoyado a 0.799 m. La bomba se monta en el soporte EX21 en posición local (0, 0.534, -0.09): sus entradas superiores coinciden con los terminales existentes y su abrazadera rodea el poste. La aplicación del montaje es idempotente y forma parte de RegionSceneBuilder.

ClinicalDeviceStatus muestra SIN SUJETO o LINEA SELLADA. El contador de revisión avanza cada ocho segundos de tiempo simulado; la pausa no lo avanza. La bomba tiene un clic local tenue, sin ráfagas acumuladas ante un frame largo. No se generan constantes vitales aleatorias. Se corrigió la orientación del texto tras detectar pantallas vacías en las primeras capturas; la textura dinámica de fuente se sincroniza también al reconstruir su atlas durante juego.

Validación: topología y conversión de coordenadas comprobadas contra Blender; capturas neutrales y de REG-S3 revisadas; 70/70 pruebas Edit Mode, job 4b5b59ae0e224ccab461894c6d71f549, 1.917 s. Esta entrega no atribuye a su código un nuevo resultado Play Mode. Evidencia visual en SourceArt/_evidence/EX-22.

Build Windows EX22-Devices: Succeeded, 284.83 MB, 51.73 s, cero errores y 55 advertencias. Registro en evidencia/build_EX22-Devices.json.

Pendientes: acabado localizado y revisión con iluminación final, conexión futura con sujetos clínicos, escucha y recorrido jugable del montaje. La bomba supera la profundidad nominal de 0.15 m contando la abrazadera posterior; requiere aceptación dimensional. Los dos assets están integrados, no declarados Conforme. Continúa pendiente el resto del catálogo.
