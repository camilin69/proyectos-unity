using Esneider.Audio;
using UnityEngine;

namespace Esneider.World
{
    // Fictional equipment self-checks. No random vital signs or implied patient data.
    public class ClinicalDeviceStatus : MonoBehaviour
    {
        public TextMesh display;
        public AudioSource clickSource;
        public string unitId = "MON-01";
        public bool isPump;
        public bool subjectConnected;
        public float checkInterval = 8f;
        public int CompletedChecks { get; private set; }
        float _elapsed;
        Material _displayMaterial;

        void OnEnable() { Font.textureRebuilt += OnFontRebuilt; RefreshDisplay(); }
        void OnDisable() { Font.textureRebuilt -= OnFontRebuilt; }
        void OnDestroy()
        {
            if (_displayMaterial) Destroy(_displayMaterial);
        }
        void OnFontRebuilt(Font font)
        {
            if (display && display.font == font && _displayMaterial)
                _displayMaterial.mainTexture = font.material.mainTexture;
        }
        void Start()
        {
            if (clickSource && AudioService.Instance) clickSource.outputAudioMixerGroup = AudioService.Instance.ambient;
        }
        void Update() { Advance(Time.deltaTime); }
        public void Advance(float seconds)
        {
            if (seconds <= 0) return;
            _elapsed += seconds;
            float interval = Mathf.Max(4f, checkInterval);
            if (_elapsed < interval) return;
            int count = Mathf.FloorToInt(_elapsed / interval); _elapsed -= count * interval;
            CompletedChecks += count; RefreshDisplay();
            // One quiet local sound even when a frame spans multiple checks.
            if (Application.isPlaying && isPump && clickSource && clickSource.clip) clickSource.PlayOneShot(clickSource.clip);
        }
        public void RefreshDisplay()
        {
            if (!display) return;
            string status = isPump ? "LINEA SELLADA" : subjectConnected ? "SUJETO CONECTADO" : "SIN SUJETO";
            display.text = unitId + "\n" + status + "\nREV " + (CompletedChecks % 10000).ToString("D4");
            if (Application.isPlaying && display.font)
            {
                if (!_displayMaterial)
                {
                    var renderer = display.GetComponent<Renderer>();
                    if (!renderer.sharedMaterial) return;
                    _displayMaterial = new Material(renderer.sharedMaterial);
                    renderer.sharedMaterial = _displayMaterial;
                }
                display.font.RequestCharactersInTexture(display.text, display.fontSize);
                OnFontRebuilt(display.font);
            }
        }
    }
}
