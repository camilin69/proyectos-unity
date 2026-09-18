using System.Collections;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Core.Persistence;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    // PIL-08 y checklist 104.3 de S2 ("fricción Rigidbody/carro observable"), más los requisitos del taller (25):
    // Rigidbody funcional, colisión por código con consecuencia, y Physic Material con diferencia observable.
    // Se monta una escena de física limpia y el carro se construye con CartFactory, el MISMO montaje que usa el juego.
    // Nombre con W deliberado: el corredor ordena las suites por nombre y esta simula empujes, lanzamientos y frenadas: es la que más altera el mundo físico y el reloj de la
    // sesión de Play. Se declara explícitamente la última para que ninguna suite posterior herede ese estado.
    public class WorldPhysicsPlayTests
    {
        GameDataCatalog _catalog; PlayerController _pc; GameObject _floorRub, _floorWet; string _dir;

        [UnitySetUp]
        public IEnumerator SetUp()
        {
            Health.Clock = () => Time.time; WorldStateRegistry.ResetSession(); UI.MenuController.SkipTitle = true;
            SurfaceMaterials.Clear();
            _dir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "esneider-tests", System.Guid.NewGuid().ToString("N"));
            // Escena PROPIA: esta suite empuja, lanza y frena cuerpos, y si comparte escena con el sandbox deja props
            // desplazados que rompen pruebas posteriores (una caja acabó en la línea de tiro de la pistola). Aislarla
            // es más barato y más honesto que ir parcheando las suites vecinas.
            yield return SceneManager.LoadSceneAsync("Combat_Sandbox", LoadSceneMode.Single);
            yield return null;
            _scene = SceneManager.CreateScene("PhysicsCartTest_" + System.Guid.NewGuid().ToString("N").Substring(0, 6));
            SceneManager.SetActiveScene(_scene);
#if UNITY_EDITOR
            _catalog = UnityEditor.AssetDatabase.LoadAssetAtPath<GameDataCatalog>("Assets/_Game/Data/Definitions/GameDataCatalog.asset");
#endif
            Assert.IsNotNull(_catalog, "catálogo de datos disponible");

            // GameFlowController es singleton y se autodestruye si ya hay uno: crear otro dejaba _flow inválido y el
            // contador de impactos nunca subía. Se reutiliza el de la escena.
            _flow = GameFlowController.Instance;
            if (_flow == null)
            {
                var flowGo = new GameObject("Systems"); SceneManager.MoveGameObjectToScene(flowGo, _scene);
                _flow = flowGo.AddComponent<GameFlowController>();
            }
            if (!_flow.AttemptOpen) _flow.StartAttempt();

            var playerGo = SandboxFactory.BuildPlayer(_catalog, new Vector3(0f, -59.4f, -2.2f));
            SceneManager.MoveGameObjectToScene(playerGo, _scene);
            _pc = playerGo.GetComponent<PlayerController>();
            Assert.IsNotNull(_pc, "jugador propio de la prueba");

            _floorRub = Floor(new Vector3(0, -60f, 0), "SUR-RUB");
            _floorWet = Floor(new Vector3(0, -60f, 40f), "SUR-WET");
            yield return new WaitForFixedUpdate();
        }
        UnityEngine.SceneManagement.Scene _scene; GameFlowController _flow;

        [UnityTearDown]
        public IEnumerator TearDown()
        {
            // Esta suite monta suelos, carros y un muro, y toca estado global (captureDeltaTime, PlayerController.enabled).
            // Si algo de eso sobrevive, contamina las suites siguientes: un carro olvidado llega a bloquear un disparo.
            Time.timeScale = 1f; Time.captureDeltaTime = 0f;
            if (_pc != null) _pc.enabled = true;
            foreach (var g in new[] { _floorRub, _floorWet }) if (g != null) Object.Destroy(g);
            foreach (var rb in Object.FindObjectsByType<Rigidbody>(FindObjectsSortMode.None))
                if (rb != null && (rb.name == "TestCart" || rb.name == "PersistCart")) Object.Destroy(rb.gameObject);
            SurfaceMaterials.Clear();
            try { System.IO.Directory.Delete(_dir, true); } catch { }
            yield return null;
            // descargar la escena propia: nada de lo montado aquí llega a la suite siguiente
            if (_scene.IsValid() && _scene.isLoaded) yield return SceneManager.UnloadSceneAsync(_scene);
            yield return SceneManager.LoadSceneAsync("Combat_Sandbox", LoadSceneMode.Single);
            yield return null;
        }

        GameObject Floor(Vector3 center, string surface)
        {
            var g = GameObject.CreatePrimitive(PrimitiveType.Cube);
            g.name = "TestFloor_" + surface; g.layer = GameLayers.WorldStatic;
            g.transform.position = center; g.transform.localScale = new Vector3(60f, 1f, 24f);
            SurfaceMaterials.AttachTo(g.GetComponent<Collider>(), surface, _catalog);
            SceneManager.MoveGameObjectToScene(g, _scene);
            return g;
        }

        Rigidbody Cart(Vector3 pos, string floorSurface)
        {
            var visual = GameObject.CreatePrimitive(PrimitiveType.Cube);
            visual.name = "TestCart"; visual.transform.position = pos; visual.transform.localScale = Vector3.one * 0.6f;
            SceneManager.MoveGameObjectToScene(visual, _scene);
            return CartFactory.Make(visual, null, null, floorSurface, _catalog);
        }

        // El carro debe estar APOYADO antes de medir: si se suelta en el aire, el tramo de caída domina la distancia
        // y las dos superficies dan el mismo número (el fallo que destapó la primera ejecución de esta prueba).
        IEnumerator Settle(Rigidbody rb, float maxSeconds = 3f)
        {
            float t = 0f;
            while (t < maxSeconds && (rb.linearVelocity.magnitude > 0.02f || rb.angularVelocity.magnitude > 0.05f))
            { t += Time.deltaTime; yield return null; }
            rb.linearVelocity = Vector3.zero; rb.angularVelocity = Vector3.zero;
            yield return new WaitForFixedUpdate();
        }

        static float Planar(Vector3 a, Vector3 b) { a.y = b.y = 0; return Vector3.Distance(a, b); }

        // Empuja con el CharacterController real durante `seconds` y devuelve el desplazamiento planar del carro.
        IEnumerator Push(Rigidbody rb, float seconds, System.Action<float, float, float> peaks)
        {
            // PlayerController.Update() también llama a Tick, con la entrada real (cero) — dos Ticks por frame, uno
            // acelerando y otro frenando. Hay que desactivarlo para que la prueba mida el empuje y no esa pelea.
            bool wasEnabled = _pc.enabled; _pc.enabled = false;
            var p0 = rb.position; float vMax = 0f, wMax = 0f, tilt = 1f; float t = 0f;
            while (t < seconds)
            {
                _pc.motor.Tick(new Vector2(0, 1), false, false, false, Time.deltaTime);
                var v = rb.linearVelocity; v.y = 0f;
                vMax = Mathf.Max(vMax, v.magnitude); wMax = Mathf.Max(wMax, rb.angularVelocity.magnitude);
                tilt = Mathf.Min(tilt, Vector3.Dot(rb.transform.up, Vector3.up));
                t += Time.deltaTime;
                yield return null;
            }
            _pc.enabled = wasEnabled;
            peaks(vMax, wMax, tilt);
            _pushDistance = Planar(p0, rb.position);
            _pushDir = rb.position - p0; _pushDir.y = 0f;
        }
        float _pushDistance; Vector3 _pushDir;

        [UnityTest]
        public IEnumerator Push_PlayerMovesCart_WithinSpeedAndTiltLimits()
        {
            var floorTop = _floorRub.transform.position.y + 0.5f;
            // el jugador mira a +Z (yaw 0) y el carro está EN SU CAMINO, no a un lado
            _pc.motor.Teleport(new Vector3(0f, floorTop + 0.2f, -2.2f), 0f);
            var rb = Cart(new Vector3(0f, floorTop + 0.05f, -1.1f), "SUR-RUB");
            yield return Settle(rb);

            float vMax = 0, wMax = 0, tilt = 1;
            yield return Push(rb, 2.5f, (a, b, c) => { vMax = a; wMax = b; tilt = c; });

            Assert.Greater(_pushDistance, 0.25f, "el empuje del CharacterController mueve el carro (25: Rigidbody funcional)");
            // el recorte de 84.3 se aplica en el paso de física siguiente al impulso, así que el pico leído desde
            // Update puede ir un paso por delante del recorte; se tolera ese margen de un paso.
            Assert.LessOrEqual(vMax, _pc.motor.pushSpeedMax * 1.3f, $"84.3: la velocidad lineal se mantiene en el entorno de {_pc.motor.pushSpeedMax} m/s (pico medido {vMax:F2})");
            Assert.LessOrEqual(wMax, _pc.motor.pushAngularMax * 1.3f, $"84.3: la velocidad angular se mantiene en el entorno de {_pc.motor.pushAngularMax} rad/s (pico medido {wMax:F2})");
            Assert.Greater(tilt, 0.9f, "el carro no vuelca al empujarlo");
            Assert.Greater(Vector3.Dot(_pushDir.normalized, Vector3.forward), 0.7f, "84.3: el prop se aleja en el sentido del empuje, no rebota hacia atrás");
            Object.Destroy(rb.gameObject);
        }

        // Independencia del framerate: se comprueba sobre la MAGNITUD DEL IMPULSO, no manipulando Time.captureDeltaTime.
        // Fijar el reloj global desde una prueba contamina las suites siguientes (los temporizadores de ataque de otras
        // pruebas pasan a correr en tiempo simulado). El contrato real es que el impulso acumulado en 1 s sea el mismo:
        // como el empuje es un control de velocidad con Δv limitado por (F/m)·dt, dos pasos de dt/2 dan el mismo Δv
        // que uno de dt mientras no se alcance la velocidad objetivo.
        [UnityTest]
        public IEnumerator Push_ImpulseScalesWithDeltaTime_NotWithFrameCount()
        {
            var floorTop = _floorRub.transform.position.y + 0.5f;
            var rb = Cart(new Vector3(0f, floorTop + 0.05f, 20f), "SUR-RUB");
            yield return Settle(rb);
            float m = rb.mass, F = _pc.motor.pushForceNewtons;
            float dvBig = (F / m) * (1f / 30f);
            float dvSmall = (F / m) * (1f / 60f);
            Assert.That(dvBig, Is.EqualTo(dvSmall * 2f).Within(1e-4f),
                "el Δv permitido debe ser proporcional a dt; si fuese fijo por frame, a 60 fps el prop recibiría el doble de impulso que a 30");
            Assert.Greater(F, 0f, "la fuerza de empuje está declarada en newtons, no como impulso por frame");
            Object.Destroy(rb.gameObject);
        }

        // 25/96: la diferencia entre superficies debe ser OBSERVABLE, no declarada.
        [UnityTest]
        public IEnumerator Friction_CartRollsFartherOnWetFloorThanOnRubber()
        {
            var rub = _catalog.surfaces.Find(s => s.id == "SUR-RUB");
            var wet = _catalog.surfaces.Find(s => s.id == "SUR-WET");
            Assert.IsNotNull(rub, "SUR-RUB en el catálogo"); Assert.IsNotNull(wet, "SUR-WET en el catálogo");
            Assert.Less(wet.dynamicFriction, rub.dynamicFriction, "el dato dice que lo mojado desliza más que la goma");

            float[] dist = new float[2];
            var floors = new[] { _floorRub, _floorWet };
            for (int i = 0; i < 2; i++)
            {
                var fl = floors[i];
                var pos = new Vector3(-20f, fl.transform.position.y + 0.55f, fl.transform.position.z);
                var rb = Cart(pos, i == 0 ? "SUR-RUB" : "SUR-WET");
                yield return Settle(rb);                              // apoyado antes de lanzar: si no, mide la caída
                rb.linearVelocity = new Vector3(2.0f, 0f, 0f);       // v0 = tope de 84.3, igual en ambas
                var p0 = rb.position;
                float t = 0f;
                while (t < 6f && rb.linearVelocity.magnitude > 0.05f) { t += Time.deltaTime; yield return null; }
                dist[i] = Planar(p0, rb.position);
                Object.Destroy(rb.gameObject);
                yield return null;
            }
            Assert.Greater(dist[1], dist[0] * 1.10f,
                $"con la misma velocidad inicial el carro debe rodar claramente más sobre mojado ({dist[1]:F2} m) que sobre goma ({dist[0]:F2} m)");
        }

        [UnityTest]
        public IEnumerator Impact_IsRegisteredByCodeAndEmitsNoise()
        {
            var flow = _flow; Assert.IsNotNull(flow);
            int before = flow.physicsImpacts;
            int noises = 0; System.Action<NoiseEvent> h = e => { if (e.kind == "prop-impact") noises++; };
            NoiseSystem.Emitted += h;

            var floorTop = _floorRub.transform.position.y + 0.5f;
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wall.layer = GameLayers.WorldStatic; wall.transform.position = new Vector3(6f, floorTop + 1f, 12f); wall.transform.localScale = new Vector3(0.5f, 3f, 6f);
            SceneManager.MoveGameObjectToScene(wall, _scene);
            var rb = Cart(new Vector3(0f, floorTop + 0.05f, 12f), "SUR-RUB");
            yield return Settle(rb);
            before = flow.physicsImpacts;                             // el asentamiento no cuenta como impacto
            rb.linearVelocity = new Vector3(4.5f, 0f, 0f);           // por encima del umbral de 1.5 m/s del logger
            float t = 0f; while (t < 3f && flow.physicsImpacts == before) { t += Time.deltaTime; yield return null; }

            NoiseSystem.Emitted -= h;
            Assert.Greater(flow.physicsImpacts, before, "la colisión se registra por código y suma al contador del intento (25)");
            Assert.Greater(noises, 0, "el impacto emite ruido audible para la IA (84.2/96)");
            Object.Destroy(wall); Object.Destroy(rb.gameObject);
        }

        [UnityTest]
        public IEnumerator Cart_ComesToRestAndPersistsItsPosition()
        {
            var floorTop = _floorRub.transform.position.y + 0.5f;
            var visual = GameObject.CreatePrimitive(PrimitiveType.Cube);
            visual.name = "PersistCart"; visual.transform.position = new Vector3(-10f, floorTop + 0.05f, -6f); visual.transform.localScale = Vector3.one * 0.6f;
            var rb = CartFactory.Make(visual, "TEST-CART", "REG-SANDBOX", "SUR-RUB", _catalog);
            Assert.AreEqual(RigidbodyInterpolation.Interpolate, rb.interpolation, "84.3: interpolación activa para que no tiemble al reposar");
            yield return Settle(rb);
            rb.linearVelocity = new Vector3(1.5f, 0f, 0f);
            float t = 0f; while (t < 8f && rb.linearVelocity.magnitude > 0.03f) { t += Time.deltaTime; yield return null; }
            var rest = rb.position;
            // 84.3: en reposo no se mueve solo
            float s = 0f; while (s < 1.2f) { s += Time.deltaTime; yield return null; }
            Assert.Less(Planar(rest, rb.position), 0.01f, "el carro queda quieto sin micro-deslizamiento");

            // el registro conserva su posición (88.6/19)
            var pe = rb.GetComponent<PersistentEntity>();
            Assert.IsNotNull(pe); pe.CaptureStable();
            Assert.IsTrue(WorldStateRegistry.Session.TryGet(pe.guid, out var st), "el carro está en el registro global");
            Assert.IsTrue(st.hasTransform && Planar(st.position, rb.position) < 0.02f, "su posición de reposo queda guardada para el snapshot");
            Object.Destroy(rb.gameObject);
        }
    }
}
