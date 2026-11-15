using System.Collections;
using UnityEngine;

namespace Dream
{
    // Una puerta que gira sobre su bisagra. La abren las cinematicas (Shot.onStart) o un recuerdo.
    public class DoorSwing : MonoBehaviour
    {
        public Transform hinge;
        public float openAngle = -100f, seconds = 2.2f;
        bool _open;

        public void Open()
        {
            if (_open) return;
            _open = true;
            StartCoroutine(Swing());
        }

        IEnumerator Swing()
        {
            var h = hinge ? hinge : transform;
            var a = h.localRotation;
            var b = a * Quaternion.Euler(0f, openAngle, 0f);
            for (float t = 0f; t < seconds; t += Time.deltaTime)
            {
                float k = t / seconds; k = k * k * (3f - 2f * k);
                h.localRotation = Quaternion.Slerp(a, b, k);
                yield return null;
            }
            h.localRotation = b;
        }
    }
}
