using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.World
{
    public class PreservationConsole : MonoBehaviour, IInteractable
    {
        public const string ConfirmedFlag = "PRESERVATION_RECORD_CONFIRMED";
        public TextMesh display;
        public AudioSource confirmationSound;
        bool _released, _confirmed;
        Material _fontMaterial;
        public string Prompt => "Confirmar registro Lázaro";
        public bool CanInteract(GameObject who) => WorldStateRegistry.Session.HasFlag("OPENING_DONE") && !WorldStateRegistry.Session.HasFlag(ConfirmedFlag);
        public void Interact(GameObject who)
        {
            if (!CanInteract(who)) return;
            if (!WorldStateRegistry.Session.SetFlag(ConfirmedFlag)) return;
            RefreshDisplay();
            if (Application.isPlaying && confirmationSound && confirmationSound.clip) confirmationSound.PlayOneShot(confirmationSound.clip);
        }
        void OnEnable() { Font.textureRebuilt += OnFontRebuilt; RefreshDisplay(); }
        void OnDisable() { Font.textureRebuilt -= OnFontRebuilt; }
        void OnDestroy() { if (_fontMaterial) Destroy(_fontMaterial); }
        void Update()
        {
            var state = WorldStateRegistry.Session;
            if (_released != state.HasFlag("OPENING_DONE") || _confirmed != state.HasFlag(ConfirmedFlag)) RefreshDisplay();
        }
        public void RefreshDisplay()
        {
            _released = WorldStateRegistry.Session.HasFlag("OPENING_DONE");
            _confirmed = WorldStateRegistry.Session.HasFlag(ConfirmedFlag);
            if (!display) return;
            display.text = _released
                ? "LÁZARO / ESNEIDER\nTIEMPO TRANSCURRIDO\n2000 AÑOS\n" + (_confirmed ? "REGISTRO CONFIRMADO" : "CONFIRMAR REGISTRO")
                : "LÁZARO / ESNEIDER\nDIAGNÓSTICO\nPRESERVACIÓN\nAPERTURA PENDIENTE";
            if (Application.isPlaying && display.font)
            {
                if (!_fontMaterial)
                {
                    var renderer = display.GetComponent<Renderer>();
                    _fontMaterial = new Material(renderer.sharedMaterial); renderer.sharedMaterial = _fontMaterial;
                }
                display.font.RequestCharactersInTexture(display.text, display.fontSize); OnFontRebuilt(display.font);
            }
        }
        void OnFontRebuilt(Font font)
        {
            if (display && display.font == font && _fontMaterial) _fontMaterial.mainTexture = font.material.mainTexture;
        }
    }
}
