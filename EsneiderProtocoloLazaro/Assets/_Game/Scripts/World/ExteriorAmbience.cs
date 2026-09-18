using Esneider.Core;
using UnityEngine;

namespace Esneider.World
{
    // 97.2 END-01/END-02 y 61.4: al abrir D29 entra aire y la reverb interior se reduce; al cruzar el umbral el patio
    // se ve más abierto que los pasillos. Interpola niebla, ambiente y luz direccional entre el interior (oscuro, niebla
    // densa) y el exterior (amanecer gris enfermo, niebla más abierta). Nunca blanco total: el paisaje sigue legible.
    public class ExteriorAmbience : MonoBehaviour
    {
        [Header("Volumen de patio (mundo)")]
        public Bounds area;
        public string doorId = "D29";
        public float blendSeconds = 3.5f;

        [Header("Interior (16: luz de terror)")]
        public Color interiorFog = new Color(0.03f, 0.035f, 0.04f);
        public float interiorFogDensity = 0.018f;
        public Color interiorAmbient = new Color(0.045f, 0.05f, 0.06f);

        [Header("Exterior (97.1: amanecer gris enfermo, metal húmedo)")]
        public Color exteriorFog = new Color(0.55f, 0.58f, 0.6f);
        public float exteriorFogDensity = 0.012f;
        public Color exteriorAmbient = new Color(0.35f, 0.38f, 0.41f);

        public Light sunLight;
        public float sunIntensityOutside = 1.05f;
        public AudioReverbZone interiorReverb;
        public float windVolume = 0.55f;
        // 97.1/61.4: cielo de amanecer nublado. El skybox azul por defecto contradice el tono; se sustituye por un
        // fondo sólido que empalma con la niebla, de modo que el horizonte se difumina en vez de cortarse.
        // "Nunca blanco total": el gris tiene que dejar leer las siluetas de las torres.
        public Color skyOutside = new Color(0.62f, 0.64f, 0.66f);

        Transform _player; AudioSource _wind, _air; float _k; bool _airPlayed; Door _door;
        Camera _cam; CameraClearFlags _camFlags; Color _camColor; bool _camSaved; Material _savedSkybox;
        public float Blend => _k;

        void Start()
        {
            var svc = Audio.AudioService.Instance;
            if (svc != null)
            {
                // lecho de viento continuo: sólo audible fuera; el aire que entra es un evento único al abrir (END-01)
                _wind = svc.Loop(gameObject, "SND-AMBI-WIND", 0f, svc.ambient, 6f, 90f);
                if (_wind == null) _wind = svc.Loop(gameObject, "SND-EXIT-Air", 0f, svc.ambient, 6f, 90f);
            }
            Apply(0f);
        }

        void Update()
        {
            if (_player == null)
            {
                var pc = FindFirstObjectByType<Player.PlayerController>();
                if (pc == null) return;
                _player = pc.transform;
            }
            if (_door == null) foreach (var d in FindObjectsByType<Door>(FindObjectsSortMode.None)) if (d.doorId == doorId) _door = d;

            // END-01: la compuerta abierta ya deja entrar el aire aunque el jugador no haya cruzado
            bool open = _door != null && _door.isOpen;
            if (open && !_airPlayed)
            {
                _airPlayed = true;
                var svc = Audio.AudioService.Instance;
                if (svc != null) svc.Play("SND-EXIT-Air", transform.position, 0.9f, 8, 0f, svc.ambient, false);
            }

            float target = area.Contains(_player.position) ? 1f : (open ? 0.25f : 0f);
            _k = Mathf.MoveTowards(_k, target, Time.deltaTime / Mathf.Max(0.1f, blendSeconds));
            Apply(_k);
        }

        void Apply(float k)
        {
            RenderSettings.fogColor = Color.Lerp(interiorFog, exteriorFog, k);
            RenderSettings.fogDensity = Mathf.Lerp(interiorFogDensity, exteriorFogDensity, k);
            RenderSettings.ambientLight = Color.Lerp(interiorAmbient, exteriorAmbient, k);
            if (sunLight != null) sunLight.intensity = Mathf.Lerp(0f, sunIntensityOutside, k);
            if (interiorReverb != null) interiorReverb.enabled = k < 0.5f;   // END-01: la reverb interior se reduce
            if (_wind != null) _wind.volume = windVolume * k;

            if (_cam == null) _cam = Camera.main;
            if (_cam != null)
            {
                if (!_camSaved) { _camFlags = _cam.clearFlags; _camColor = _cam.backgroundColor; _savedSkybox = RenderSettings.skybox; _camSaved = true; }
                if (k > 0.01f)
                {
                    _cam.clearFlags = CameraClearFlags.SolidColor;
                    _cam.backgroundColor = Color.Lerp(interiorFog, skyOutside, k);
                    RenderSettings.skybox = null;
                }
                else { _cam.clearFlags = _camFlags; _cam.backgroundColor = _camColor; RenderSettings.skybox = _savedSkybox; }
            }
        }

        // Al restaurar un checkpoint anterior al escape el mundo vuelve a ser interior sin transición visible.
        public void ResetToInterior() { _k = 0f; _airPlayed = false; Apply(0f); }
    }
}
