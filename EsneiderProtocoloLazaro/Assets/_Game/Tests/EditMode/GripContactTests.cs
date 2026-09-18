using System.Collections.Generic;
using Esneider.Player;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    // 64 / PIL-14 · "palma, pulgar y dedos sostienen el grip" medido, no supuesto.
    //
    // Dos defectos reales que esta medición destapó y que ninguna prueba anterior podía ver:
    //   1) los tres puntos de agarre escritos a mano tenían el signo de Z invertido respecto del eje de exportación
    //      del FBX, así que el arma quedaba sujeta por el extremo contrario: la varilla a 375 mm de la palma, la
    //      escopeta a 173 y la pistola a 83, con las puntas de los dedos entre 160 y 466 mm del mango;
    //   2) cada dedo era una pieza rígida con un solo hueso, de modo que al cerrar el puño giraba entero alrededor
    //      del nudillo y la punta pasaba de largo del mango en vez de envolverlo.
    //
    // La prueba reproduce exactamente la colocación que hace ViewmodelController y mide sobre la malla deformada.
    public class GripContactTests
    {
        const float PalmTol = 0.040f;        // el centro del mango tiene que caer en la palma
        const float ReachTol = 0.035f;       // la yema llega a la superficie del mango
        const float ThumbTol = 0.055f;       // el pulgar se opone desde el otro lado, no cierra tanto
        const float PenetrationTol = 0.010f; // la yema aplasta contra el mango, no lo atraviesa

        // Asiento del mango respecto al centro de la pieza de la palma, el mismo que usa ViewmodelController.
        static readonly Vector3 GripSeat = new Vector3(0f, 0.021f, 0.032f);

        struct Arma { public string prefab; public Vector3 reserva; public Quaternion rot; }

        static readonly Arma[] Armas =
        {
            new Arma { prefab = "WPN-01_Crowbar", reserva = new Vector3(0f, 0f, -0.175f), rot = Quaternion.Euler(-60f, 10f, 0f) },
            new Arma { prefab = "WPN-02_Pistol",  reserva = new Vector3(0f, -0.041f, -0.038f), rot = Quaternion.identity },
            new Arma { prefab = "WPN-03_Shotgun", reserva = new Vector3(0f, -0.045f, -0.082f), rot = Quaternion.identity },
        };

        [Test]
        public void WeaponsSitInThePalmAndTheFingersCloseOnTheGrip()
        {
            var problemas = new List<string>();
            var resumen = new List<string>();

            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Player/CHR-01_Arms.prefab");
            Assert.IsNotNull(prefab, "falta el prefab de los brazos");
            var arms = Object.Instantiate(prefab);
            arms.transform.position = Vector3.zero;
            arms.transform.rotation = Quaternion.identity;
            try
            {
                if (arms.GetComponent<Animator>() == null) arms.AddComponent<Animator>();
                var grip = FindClip("CHR-01_Arms", "Arms_Grip");
                Assert.IsNotNull(grip, "falta el clip Arms_Grip");
                grip.SampleAnimation(arms, grip.length);   // puño cerrado

                Transform hand = null;
                foreach (var t in arms.GetComponentsInChildren<Transform>(true))
                    if (t.name == "hand_R" && t.parent != null && t.parent.name == "forearm_R") hand = t;
                Assert.IsNotNull(hand, "falta el hueso hand_R");
                Renderer palmaMesh = null;
                foreach (var r in arms.GetComponentsInChildren<Renderer>(true)) if (r.name == "palm_R") palmaMesh = r;
                Assert.IsNotNull(palmaMesh, "falta la pieza palm_R");
                var asientoLocal = hand.InverseTransformPoint(palmaMesh.bounds.center) + GripSeat;
                var palma = hand.TransformPoint(asientoLocal);

                foreach (var arma in Armas)
                {
                    var wprefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Weapons/" + arma.prefab + ".prefab");
                    Assert.IsNotNull(wprefab, "falta el prefab " + arma.prefab);
                    var w = Object.Instantiate(wprefab, hand);
                    try
                    {
                        var punto = ViewmodelController.GripPoint(w, arma.reserva);
                        w.transform.localRotation = arma.rot;
                        w.transform.localPosition = asientoLocal - (arma.rot * punto);

                        var mango = GripVertices(w);
                        if (mango.Count == 0) { problemas.Add(arma.prefab + " no declara ninguna pieza de mango"); continue; }

                        var centro = Vector3.zero;
                        foreach (var p in mango) centro += p;
                        centro /= mango.Count;
                        float aPalma = (centro - palma).magnitude;
                        if (aPalma > PalmTol)
                            problemas.Add(string.Format("{0}: el mango queda a {1:F0} mm de la palma (máximo {2:F0})",
                                arma.prefab, aPalma * 1000f, PalmTol * 1000f));

                        Vector3 eje; float radio, medio;
                        GripAxis(mango, centro, out eje, out radio, out medio);

                        var detalle = new List<string>();
                        foreach (var smr in arms.GetComponentsInChildren<SkinnedMeshRenderer>(true))
                        {
                            bool dedo = smr.name.StartsWith("finger_R");
                            bool pulgar = smr.name.StartsWith("thumb_R");
                            if (!dedo && !pulgar) continue;
                            // sólo la falange distal: es la yema la que toca el mango
                            if (dedo && !smr.name.EndsWith("c")) continue;
                            if (pulgar && !smr.name.EndsWith("b")) continue;

                            var yema = Tip(smr, hand.position);
                            // Distancia a la SUPERFICIE del cilindro, no al vértice más cercano: el mango de la
                            // varilla mide 170 mm con pocos anillos, así que "el vértice más cercano" exagera la
                            // separación hasta 15 mm y convierte un agarre correcto en un fallo.
                            float radial = Vector3.ProjectOnPlane(yema - centro, eje).magnitude;
                            float axial = Mathf.Abs(Vector3.Dot(yema - centro, eje));
                            float fueraDelTramo = Mathf.Max(0f, axial - medio);
                            float alcance = Mathf.Sqrt(Mathf.Max(0f, radial - radio) * Mathf.Max(0f, radial - radio)
                                                       + fueraDelTramo * fueraDelTramo);
                            float dentro = axial <= medio ? Mathf.Max(0f, radio - radial) : 0f;

                            detalle.Add(string.Format("{0} a {1:F0} mm ({2:F0} dentro)", smr.name, alcance * 1000f, dentro * 1000f));
                            float tol = pulgar ? ThumbTol : ReachTol;
                            if (alcance > tol)
                                problemas.Add(string.Format("{0}: {1} se queda a {2:F0} mm del mango (máximo {3:F0})",
                                    arma.prefab, smr.name, alcance * 1000f, tol * 1000f));
                            if (dentro > PenetrationTol)
                                problemas.Add(string.Format("{0}: {1} atraviesa el mango {2:F0} mm (máximo {3:F0})",
                                    arma.prefab, smr.name, dentro * 1000f, PenetrationTol * 1000f));
                        }
                        resumen.Add(string.Format("{0}: mango a {1:F0} mm de la palma, radio {2:F0} mm; {3}",
                            arma.prefab, aPalma * 1000f, radio * 1000f, string.Join(", ", detalle.ToArray())));
                    }
                    finally { Object.DestroyImmediate(w); }
                }
            }
            finally { Object.DestroyImmediate(arms); }

            Debug.Log("Agarre medido sobre la malla deformada:\n  " + string.Join("\n  ", resumen.ToArray()));
            Assert.IsEmpty(problemas, string.Join("\n", problemas.ToArray()));
        }

        static AnimationClip FindClip(string asset, string nombre)
        {
            foreach (var o in AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/" + asset + ".fbx"))
            {
                var c = o as AnimationClip;
                if (c != null && !c.name.StartsWith("__") && c.name == nombre) return c;
            }
            return null;
        }

        static List<Vector3> GripVertices(GameObject weapon)
        {
            var pts = new List<Vector3>();
            foreach (var mf in weapon.GetComponentsInChildren<MeshFilter>(true))
            {
                if (mf.sharedMesh == null || mf.name.IndexOf("grip", System.StringComparison.OrdinalIgnoreCase) < 0) continue;
                foreach (var v in mf.sharedMesh.vertices) pts.Add(mf.transform.TransformPoint(v));
            }
            return pts;
        }

        // El mango es un cilindro. Su eje es la recta que une los dos vértices más separados de la nube: probar sólo
        // los ejes del mundo falla en cuanto el arma va girada, que es el caso de la varilla.
        static void GripAxis(List<Vector3> pts, Vector3 centro, out Vector3 eje, out float radio, out float medio)
        {
            var lejano = pts[0]; float d0 = -1f;
            foreach (var p in pts) { float d = (p - centro).sqrMagnitude; if (d > d0) { d0 = d; lejano = p; } }
            var opuesto = pts[0]; float d1 = -1f;
            foreach (var p in pts) { float d = (p - lejano).sqrMagnitude; if (d > d1) { d1 = d; opuesto = p; } }
            eje = (opuesto - lejano).normalized;
            medio = 0f;
            var radiales = new List<float>();
            foreach (var p in pts)
            {
                radiales.Add(Vector3.ProjectOnPlane(p - centro, eje).magnitude);
                medio = Mathf.Max(medio, Mathf.Abs(Vector3.Dot(p - centro, eje)));
            }
            radiales.Sort();
            radio = radiales.Count > 0 ? radiales[radiales.Count / 2] : 0f;
        }

        static Vector3 Tip(SkinnedMeshRenderer smr, Vector3 desde)
        {
            var baked = new Mesh();
            smr.BakeMesh(baked, true);
            var tip = Vector3.zero; float lejos = -1f;
            foreach (var v in baked.vertices)
            {
                var wv = smr.transform.TransformPoint(v);
                float d = (wv - desde).magnitude;
                if (d > lejos) { lejos = d; tip = wv; }
            }
            Object.DestroyImmediate(baked);
            return tip;
        }
    }
}
