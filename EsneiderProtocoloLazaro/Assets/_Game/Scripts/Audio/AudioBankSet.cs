using System;
using System.Collections.Generic;
using UnityEngine;

namespace Esneider.Audio
{
    [Serializable]
    public class AudioBank { public string id; public AudioClip[] clips; }

    // Bancos por ID de muestra (72.2). Se rellena desde Assets/_Game/Audio/** por el editor; el runtime no busca por nombre cada vez.
    [CreateAssetMenu(menuName = "Esneider/Audio/Bank Set", fileName = "AudioBankSet")]
    public class AudioBankSet : ScriptableObject
    {
        public List<AudioBank> banks = new List<AudioBank>();
        public void ApplyTo(AudioService s) { foreach (var b in banks) s.RegisterBank(b.id, b.clips); }
    }
}
