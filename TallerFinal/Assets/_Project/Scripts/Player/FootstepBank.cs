using UnityEngine;

namespace Dream
{
    // Grabaciones de una superficie. Cada paso elige una distinta a la anterior, con tono y volumen aleatorios.
    [CreateAssetMenu(menuName = "Sueno Lucido/Banco de pasos")]
    public class FootstepBank : ScriptableObject
    {
        public SurfaceType surface;
        public AudioClip[] clips;
        [Range(0f, 1f)] public float volume = 0.55f;
        public Vector2 pitch = new(0.92f, 1.08f);
        public Vector2 volumeJitter = new(0.8f, 1f);

        int _last = -1;

        public AudioClip Pick()
        {
            if (clips == null || clips.Length == 0) return null;
            if (clips.Length == 1) return clips[0];
            int i;
            do i = Random.Range(0, clips.Length); while (i == _last);
            _last = i;
            return clips[i];
        }
    }
}
