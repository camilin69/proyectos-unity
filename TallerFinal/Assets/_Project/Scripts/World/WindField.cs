using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace Dream
{
    // Vegetacion dibujada por instancing y mecida por el viento. Cada mata se inclina desde su base en la direccion del
    // viento, con su propia fase (no se mueven al unisono) y mas cuando sopla una rafaga. Solo se dibuja lo cercano
    // a la camara, y a partir de cierta distancia se aclara, para que la GPU integrada aguante miles de matas.
    public class WindField : MonoBehaviour
    {
        [Serializable]
        public class Batch
        {
            public Mesh mesh;
            public Material[] materials;
            public Vector3[] basePoints;          // punto del suelo donde nace la mata (pivote del vaiven)
            public Matrix4x4[] matrices;          // pose en reposo
            public float stiffness = 1f;          // 1 pasto, 0.3 arbustos
            public bool castShadows;
        }

        public List<Batch> batches = new();
        public float drawDistance = 42f, thinFrom = 18f, maxBendDeg = 14f;
        [Tooltip("Rafagas que se ven recorrer el campo: separacion (1/m), velocidad (m/s) y fuerza")]
        public float gustScale = 0.09f, gustSpeed = 6f, gustStrength = 1.3f;

        readonly Matrix4x4[] _buffer = new Matrix4x4[1023];
        RenderParams[] _params;

        void Update()
        {
            var cam = Camera.main;
            if (!cam) return;
            var cp = cam.transform.position;
            float t = Time.time, wind = Wind.Strength;
            var axis = Vector3.Cross(Vector3.up, Wind.Direction).normalized;
            float d2 = drawDistance * drawDistance, thin2 = thinFrom * thinFrom;
            foreach (var b in batches)
            {
                if (!b.mesh || b.matrices == null) continue;
                int n = 0;
                var bounds = new Bounds(cp, Vector3.one * drawDistance * 2f);
                for (int i = 0; i < b.matrices.Length; i++)
                {
                    var bp = b.basePoints[i];
                    float dx = bp.x - cp.x, dz = bp.z - cp.z, dd = dx * dx + dz * dz;
                    if (dd > d2) continue;
                    // a lo lejos se dibuja solo una de cada dos o tres matas
                    if (dd > thin2 && (i % (dd > thin2 * 2.5f ? 3 : 2)) != 0) continue;
                    float phase = bp.x * 0.37f + bp.z * 0.23f;
                    float sway = (Mathf.Sin(t * 1.7f + phase) * 0.55f + Mathf.Sin(t * 3.1f + phase * 1.7f) * 0.2f + 0.65f) * wind;
                    // corrientes de aire: bandas de rafaga que viajan a favor del viento y doblan el pasto al pasar
                    float along = bp.x * Wind.Direction.x + bp.z * Wind.Direction.z;
                    float across = bp.x * axis.x + bp.z * axis.z;
                    float band = Mathf.Sin(along * gustScale - t * gustSpeed * gustScale + Mathf.Sin(across * 0.05f) * 2f);
                    sway += Mathf.Pow(Mathf.Max(0f, band), 6f) * gustStrength;
                    var rot = Quaternion.AngleAxis(sway * maxBendDeg * b.stiffness, axis);
                    _buffer[n++] = Matrix4x4.Translate(bp) * Matrix4x4.Rotate(rot) * Matrix4x4.Translate(-bp) * b.matrices[i];
                    if (n == _buffer.Length) { Draw(b, n, bounds); n = 0; }
                }
                if (n > 0) Draw(b, n, bounds);
            }
        }

        void Draw(Batch b, int n, Bounds bounds)
        {
            for (int s = 0; s < b.materials.Length && s < b.mesh.subMeshCount; s++)
            {
                var rp = new RenderParams(b.materials[s])
                {
                    worldBounds = bounds,
                    shadowCastingMode = b.castShadows ? ShadowCastingMode.On : ShadowCastingMode.Off,
                    receiveShadows = true,
                    layer = gameObject.layer
                };
                Graphics.RenderMeshInstanced(rp, b.mesh, s, _buffer, n);
            }
        }
    }
}
